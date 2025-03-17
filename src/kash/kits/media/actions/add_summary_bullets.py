from chopdiff.html.html_in_md import div_wrapper

from kash.actions.core.summarize_as_bullets import summarize_as_bullets
from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_text_doc
from kash.model import Format, Item, ItemType
from kash.utils.common.type_utils import not_none

log = get_logger(__name__)


SUMMARY = "summary"
"""Class name for the summary."""

ORIGINAL = "original"
"""Class name for the original content."""


@kash_action(
    precondition=is_text_doc,
)
def add_summary_bullets(item: Item) -> Item:
    """
    Add a summary of the content (from `summarize_as_bullets`) above the full text of the item,
    with each wrapped in a div.
    """
    summary_item = summarize_as_bullets(item)

    wrap_summary = div_wrapper(class_name=SUMMARY)
    wrap_original = div_wrapper(class_name=ORIGINAL)

    combined_body = (
        wrap_summary(not_none(summary_item.body)) + "\n\n" + wrap_original(not_none(item.body))
    )

    output_item = item.derived_copy(
        type=ItemType.doc,
        format=Format.md_html,
        body=combined_body,
    )

    return output_item
