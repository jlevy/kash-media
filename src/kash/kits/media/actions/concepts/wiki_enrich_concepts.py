from strif import abbrev_str

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_concept
from kash.kits.media.wiki.wiki_search import wiki_article_search
from kash.model import ONE_OR_MORE_ARGS, ActionInput, ActionResult, Item

log = get_logger(__name__)


@kash_action(
    expected_args=ONE_OR_MORE_ARGS,
    precondition=is_concept,
)
def wiki_enrich_concepts(input: ActionInput) -> ActionResult:
    """
    Look at concepts without a url or body and see if they closely match a Wikipedia page.
    Does nothing if concepts already have a URL or body or no page unambiguously matches.
    """

    changed_items: list[Item] = []
    for item in input.items:
        if not item.title:
            log.warning("Skipping concept because it has no title: %s", item)
            continue
        if item.url or item.has_body:
            log.message(
                "Skipping concept because it already has a URL or body: %r: url=%s body=%s",
                item.title,
                item.url,
                abbrev_str(item.body or ""),
            )
            continue

        search_results = wiki_article_search(item.title)

        if search_results.has_unambigous_match and search_results.page_results:
            page = search_results.page_results[0].page
            log.info("Found unambiguous wiki match: %r -> %r", item.title, page.title)

            summary = page.summary
            if not summary.strip():
                log.warning(
                    "Unexpected empty summary for Wikipedia page: %r: %r", page.title, summary
                )
                continue

            # Update the url and body.
            item.body = summary
            item.url = page.canonicalurl

            log.message(
                "Updated concept %s with summary from Wikipedia page: %s",
                item.title,
                abbrev_str(summary),
            )
            changed_items.append(item)
        else:
            log.info("No unambiguous Wikipedia match found for concept '%s'", item.title)

    # Return changed items so they will be saved.
    return ActionResult(items=changed_items)
