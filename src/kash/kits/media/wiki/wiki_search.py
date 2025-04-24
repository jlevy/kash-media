from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
import wikipediaapi
from tenacity import retry, stop_after_attempt, wait_random_exponential
from thefuzz import fuzz
from typing_extensions import override
from wikipediaapi import Namespace, Wikipedia, WikipediaPage

from kash.config.logger import get_logger
from kash.web_content.file_cache_utils import cache_file
from kash.web_content.local_file_cache import Loadable

log = get_logger(__name__)


class CachingSession(requests.Session):
    def __init__(self):
        super().__init__()

    @override
    def get(self, url: str | bytes, **kwargs: Any) -> Any:
        # Extract params for cache key generation if present
        params = kwargs.get("params")
        # We need a unique key for the cache, so we use the URL and params.
        url_str = url.decode() if isinstance(url, bytes) else str(url)
        query_string = urlencode(params or {})
        url_key = f"{url_str}?{query_string}" if query_string else url_str

        orig_session = super()

        def save(path: Path):
            response = orig_session.get(url, **kwargs)
            response.raise_for_status()
            response.raw.decode_content = True
            with open(path, "wb") as f:
                f.write(response.content)

        path, was_cached = cache_file(Loadable(url_key, save))
        if was_cached:
            log.warning("Wikipedia API cache hit: %s", url_key)

        # A simple hack to make sure response.json() works.
        response = requests.Response()
        response.status_code = 200
        response.encoding = "utf-8"
        response._content = path.read_bytes()
        return response


WIKI_LANGUAGE = "en"


def get_wiki_api_base_url(language: str = WIKI_LANGUAGE) -> str:
    return f"https://{language}.wikipedia.org/w/api.php"


_wiki: Wikipedia = wikipediaapi.Wikipedia(
    language=WIKI_LANGUAGE, user_agent=wikipediaapi.USER_AGENT
)

# Hot patch the session to use our caching session.
_wiki._session = CachingSession()  # pyright: ignore[reportPrivateUsage]


@dataclass(frozen=True)
class WikiPageResult:
    """
    Holds results for a Wikipedia page query and some scoring for the page
    and the match.
    """

    page: WikipediaPage
    title_score: float

    @cached_property
    def notability_score(self) -> float:
        return calculate_notability_score(self.page)

    @cached_property
    def total_score(self) -> float:
        return self.title_score * self.notability_score / 100.0

    def score_str(self) -> str:
        return f"score {self.total_score:.2f} (title {self.title_score:.1f}, notability {self.notability_score:.2f})"


@dataclass(frozen=True)
class WikiSearchResults:
    has_unambigous_match: bool = False
    """The first result title unambiguously matches the query."""

    disambiguation_page: WikipediaPage | None = None
    """There was a disambiguation page with a fuzzy match to the query."""

    page_results: list[WikiPageResult] = field(default_factory=list)
    """All results each with a simple fuzzy match score."""

    def __bool__(self) -> bool:
        return bool(self.page_results)


def _assemble_search_results(
    concept: str,
    pages: list[WikipediaPage],
    min_notability_score: float = 4.0,
    min_title_score: float = 2.0,
    unambiguous_threshold: float = 6.0,
    unambiguous_cutoff: float = 2,
) -> WikiSearchResults:
    results: list[WikiPageResult] = []

    # Assemble results, excluding any disambiguation pages.
    disambiguation_page = None
    for page in pages:
        if wiki_is_disambiguation_page(page):
            if not disambiguation_page:
                disambiguation_page = page
            continue
        if wiki_is_list_page(page):
            continue
        if calculate_notability_score(page) < min_notability_score:
            continue
        results.append(WikiPageResult(page=page, title_score=wiki_title_score(concept, page)))

    # Is there a single, notable page that matches the query?
    if disambiguation_page:
        is_unambiguous = False
    elif len(results) == 0:
        is_unambiguous = False
    elif len(results) == 1:
        is_unambiguous = True
    else:
        sorted_results = sorted(results, key=lambda x: x.title_score, reverse=True)
        if sorted_results[0] != results[0]:
            is_unambiguous = False
        else:
            # Compare top two matches
            max_score = sorted_results[0].total_score
            second_score = sorted_results[1].total_score
            log.info(
                "Top two scores: %s (%s), %s (%s)",
                sorted_results[0].page.title,
                sorted_results[0].score_str(),
                sorted_results[1].page.title,
                sorted_results[1].score_str(),
            )
            is_unambiguous = (
                max_score > unambiguous_threshold
                and (max_score - second_score) > unambiguous_cutoff
            )

    return WikiSearchResults(
        has_unambigous_match=is_unambiguous,
        disambiguation_page=disambiguation_page,
        page_results=results,
    )


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
def wiki_article_search_raw(
    concept: str, *, max_results: int = 5, timeout: float = 10
) -> list[WikipediaPage]:
    """
    Finds Wikipedia pages related to a concept using MediaWiki API search.
    """
    try:
        # Use direct API call for search as wikipediaapi doesn't have a search method.
        # Could use nlpia2-wikipedia but it seems a bit buggy and this is more straightforward.
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": concept,
            "srlimit": max_results,
            "format": "json",
        }

        # Use our own patched caching session.
        response = _wiki._session.get(  # pyright: ignore[reportPrivateUsage]
            get_wiki_api_base_url(), params=search_params, timeout=timeout
        )
        response.raise_for_status()
        search_data = response.json()

        titles = [item["title"] for item in search_data.get("query", {}).get("search", [])]
        if not titles:
            log.warning("No search results found for concept: %r", concept)
            return []

        results: list[WikipediaPage] = []
        for title in titles:
            # Check page existence *before* scoring to avoid issues with missing/redirected pages
            page = _wiki.page(title)
            if not page.exists():
                log.debug(
                    "Page '%s' for concept '%s' does not exist or is a redirect loop.",
                    title,
                    concept,
                )
                continue
            # Ensure we get the final title after potential redirects
            final_title = page.title
            # Fetch page again with potentially redirected title to ensure consistency
            page = _wiki.page(final_title)
            if not page.exists():  # Double check after redirect resolution
                log.warning(
                    "Redirected page '%s' for concept '%s' does not exist.", final_title, concept
                )
                continue

            results.append(page)

        if not results:
            log.warning("No valid pages found after checking existence for concept: %r", concept)
            return []

        return results
    except requests.exceptions.RequestException as e:
        log.error("Wikipedia search: network error: %r: %s", concept, e)
        raise
    except Exception as e:
        log.error("Wikipedia search: unexpected error: %r: %s", concept, e)
        raise


def wiki_article_search(concept: str) -> WikiSearchResults:
    """
    Search Wikipedia for a concept and return results with additional scoring
    and disambiguation checks.
    """
    results = wiki_article_search_raw(concept)
    return _assemble_search_results(concept, results)


def wiki_title_score(concept: str, page: WikipediaPage) -> float:
    """
    Calculate the fuzzy match between a concept and a Wikipedia page title.
    """
    s1 = concept.lower()
    s2 = page.title.lower()
    return 0.5 * fuzz.ratio(s1, s2) + 0.5 * fuzz.partial_ratio(s1, s2)


def wiki_is_disambiguation_page(page: WikipediaPage) -> bool:
    """
    Check if a Wikipedia page is a disambiguation page.
    """
    return "disambiguation" in page.title.lower()


def wiki_is_list_page(page: WikipediaPage) -> bool:
    """
    Check if a Wikipedia page is a list page.
    """
    return "list of" in page.title.lower()


def calculate_notability_score(page: WikipediaPage) -> float:
    """
    Calculates a notability score for a Wikipedia page.

    Higher scores suggest a more canonical or significant page.
    This is a heuristic based on backlinks, language links, and length.
    Pages not in the main namespace get a score of 0.
    """
    if not page.exists() or page.namespace != Namespace.MAIN:
        return 0.0

    # Fetch properties; these might trigger API calls if not cached
    try:
        # FIXME: wikipediaapi's backlinks() method has no limit to how many backlinks it will fetch!
        # Should patch to limit to a few pages. Pages like "Paris" have thousands of backlinks.
        num_backlinks = len(page.backlinks)
        num_langlinks = len(page.langlinks)
        page_length = page.length or 0
    except Exception as e:
        log.error("Wikipedia search: error fetching properties for '%s': %s", page.title, e)
        raise

    # Combine metrics. This is a simple heuristic.
    # Using logarithms to temper the effect of very large numbers.
    # Adding 1 to avoid log(0). Weights can be adjusted.
    # Weight backlinks and langlinks higher.
    score = (
        math.log1p(num_backlinks) * 0.5
        + math.log1p(num_langlinks) * 0.4
        + math.log1p(page_length) * 0.1
    )

    return score

    return score
