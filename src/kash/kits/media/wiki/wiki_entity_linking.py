from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from kash.config.logger import get_logger
from kash.kits.media.wiki.wiki_search import wiki_article_search
from kash.text_handling.markdown_utils import find_markdown_text, markdown_link
from kash.utils.common.url import Url

log = get_logger(__name__)


@dataclass(frozen=True)
class EnrichmentStats:
    found_in_wikipedia: int
    found_in_text: int
    links_added: int


def link_wiki_entities(text: str, entity_strs: Sequence[str]) -> tuple[str, EnrichmentStats]:
    """
    Embed Wikipedia links for the first occurrence of each entity
    string in `text`.

    The does a case-insensitive search for each candidate entity in order,
    skipping sections already part of a link. Then uses `wiki_article_search()`
    to find a Wikipedia page and embeds a link if it is found and unambiguous.
    """

    found_in_wikipedia = 0
    found_in_text = 0
    links_added = 0

    enriched_text = text

    for entity in entity_strs:
        if not entity:
            raise ValueError("Empty entity")

        # Case‑insensitive search, skipping sections already part of a link.
        pattern = re.compile(re.escape(entity), re.IGNORECASE)
        match = find_markdown_text(pattern, enriched_text)

        if match is None:
            continue

        found_in_text += 1

        wiki_results = wiki_article_search(entity)
        if not wiki_results:
            continue
        if not wiki_results.has_unambigous_match:
            log.warning("Ambiguous Wikipedia result for %r, will skip: %r", entity, wiki_results)
            continue

        page = wiki_results.page_results[0].page
        url = page.canonicalurl
        if not url:
            log.warning("No canonical URL found for Wikipedia page: %r", page)
            continue

        found_in_wikipedia += 1

        # Use the exact matched substring to preserve the original casing.
        matched_text = match.group(0)
        replacement = markdown_link(matched_text, Url(url))

        # Replace only this first occurrence.
        enriched_text = enriched_text[: match.start()] + replacement + enriched_text[match.end() :]
        links_added += 1

    return enriched_text, EnrichmentStats(found_in_wikipedia, found_in_text, links_added)
