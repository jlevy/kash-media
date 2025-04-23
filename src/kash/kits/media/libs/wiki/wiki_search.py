from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any
from urllib.parse import urlencode

import requests
import wikipediaapi
from tenacity import retry, stop_after_attempt, wait_random_exponential
from thefuzz import fuzz
from wikipediaapi import Namespace, Wikipedia, WikipediaPage

from kash.config.logger import get_logger
from kash.utils.common.url import Url
from kash.web_content.file_cache_utils import cache_api_response

log = get_logger(__name__)

WIKI_LANGUAGE = "en"

_wiki = wikipediaapi.Wikipedia(language=WIKI_LANGUAGE, user_agent=wikipediaapi.USER_AGENT)


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


def assemble_search_results(
    concept: str,
    pages: list[WikipediaPage],
    min_notability_score: float = 4.0,
    min_title_score: float = 2.0,
    unambiguous_threshold: float = 6.0,
    unambiguous_cutoff: float = 2,
) -> WikiSearchResults:
    results = []

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
                "Top two scores: %s, %s",
                sorted_results[0].score_str(),
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


def call_wiki_api(wiki: Wikipedia, params: dict[str, Any], timeout: float = 10) -> Any:
    """
    Call the MediaWiki API with the given base URL and parameters.
    """

    base_url = f"https://{wiki.language}.wikipedia.org/w/api.php"
    log.info("Wikipedia search request: %s with params %r", base_url, params)
    response = wiki._session.get(  # pyright: ignore[reportPrivateUsage]
        base_url, params=params, timeout=timeout
    )
    response.raise_for_status()
    return response.json()


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
def wiki_article_search_api(
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

        base_url = f"https://{_wiki.language}.wikipedia.org/w/api.php"
        url = Url(f"{base_url}?{urlencode(search_params)}")
        search_data, was_cached = cache_api_response(url)
        if was_cached:
            log.message("Wikipedia search: cache hit for %r", concept)

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
    results = wiki_article_search_api(concept)
    return assemble_search_results(concept, results)


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
