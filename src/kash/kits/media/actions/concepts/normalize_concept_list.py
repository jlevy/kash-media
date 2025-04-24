from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_markdown_list
from kash.kits.media.libs.concept_utils import concepts_from_bullet_points
from kash.model import Format, Item, ItemType
from kash.text_handling.markdown_utils import as_bullet_points
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


@kash_action(
    precondition=is_markdown_list,
)
def normalize_concept_list(item: Item) -> Item:
    """
    Normalize, capitalize, sort, and remove duplicates from a Markdown list of concepts.
    """
    if not item.body:
        raise InvalidInput("Item must have a body")

    body = as_bullet_points(concepts_from_bullet_points(item.body))

    output_item = item.derived_copy(
        type=ItemType.doc,
        format=Format.markdown,
        body=body,
    )

    return output_item
