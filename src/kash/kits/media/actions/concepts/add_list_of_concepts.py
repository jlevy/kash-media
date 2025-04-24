from chopdiff.html import div_wrapper

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_text_doc
from kash.kits.media.actions.concepts.identify_concepts import identify_concepts
from kash.model import Format, Item, ItemType
from kash.utils.common.type_utils import not_none

log = get_logger(__name__)

CONCEPTS = "concepts"
"""Class name for a list of concepts."""

ORIGINAL = "original"
"""Class name for the original content."""


@kash_action(
    precondition=is_text_doc,
)
def add_list_of_concepts(item: Item) -> Item:
    """
    Add a list of concepts found in the content above the full text of the item,
    with each wrapped in a div.
    """
    # Get concepts from the text.
    concepts_item = identify_concepts(item)

    # Combine the concepts and original content with divs.
    wrap_concepts = div_wrapper(class_name=CONCEPTS)
    wrap_original = div_wrapper(class_name=ORIGINAL)
    combined_body = (
        wrap_concepts(not_none(concepts_item.body)) + "\n\n" + wrap_original(not_none(item.body))
    )

    output_item = item.derived_copy(
        type=ItemType.doc,
        format=Format.md_html,
        body=combined_body,
    )

    return output_item
