from kash.config.text_styles import COLOR_WARN, STYLE_HEADING, STYLE_HINT, STYLE_KEY
from kash.exec.command_registry import kash_command
from kash.kits.media.libs.wiki.wiki_search import WikiPageResult, wiki_article_search
from kash.shell.output.shell_output import cprint


@kash_command
def wiki_search(query: str, all: bool = False) -> None:
    """
    Search Wikipedia for a query.

    :param all: Show all results, even if there seems to be a single unambiguous match.
    """
    results = wiki_article_search(query)
    if not results:
        cprint("No results found", style=COLOR_WARN)
        return

    def show_page(result: WikiPageResult):
        page = result.page
        cprint(f"{page.title}", style=STYLE_HEADING)
        cprint(
            f"{page.canonicalurl} (pageid {page.pageid})",
            style=STYLE_HINT,
        )
        cprint(result.score_str(), style=STYLE_KEY)
        cprint(page.summary)
        cprint()

    if results.has_unambigous_match and not all:
        cprint(
            f"result unambiguous for {query!r}: ({results.page_results[0].page.title})",
            style=STYLE_HINT,
        )
        show_page(results.page_results[0])
    else:
        cprint(
            f"there are multiple reasonable matches for {query!r}: {results.disambiguation_page.title if results.disambiguation_page else 'no disambiguation page'}",
            style=STYLE_HINT,
        )
        for page_result in results.page_results:
            show_page(page_result)
