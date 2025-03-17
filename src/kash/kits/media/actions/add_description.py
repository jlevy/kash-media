from chopdiff.html.html_in_md import div_wrapper

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_text_doc
from kash.kits.media.actions.describe_briefly import describe_briefly
from kash.model import Format, Item, ItemType
from kash.utils.common.type_utils import not_none

log = get_logger(__name__)

DESCRIPTION = "description"
"""Class name for the description."""

ORIGINAL = "original"
"""Class name for the original content."""


@kash_action(
    precondition=is_text_doc,
)
def add_description(item: Item) -> Item:
    """
    Add a brief description (from `describe_briefly`) of the content above the full text of
    a document, with each wrapped in a div.
    """
    description_item = describe_briefly(item)

    wrap_description = div_wrapper(class_name=DESCRIPTION)
    wrap_original = div_wrapper(class_name=ORIGINAL)

    combined_body = (
        wrap_description(not_none(description_item.body))
        + "\n\n"
        + wrap_original(not_none(item.body))
    )

    output_item = item.derived_copy(
        type=ItemType.doc,
        format=Format.md_html,
        body=combined_body,
    )

    return output_item
