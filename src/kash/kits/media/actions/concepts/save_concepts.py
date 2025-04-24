from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_markdown_list
from kash.kits.media.libs.concept_utils import concepts_from_bullet_points
from kash.model import (
    ONE_OR_MORE_ARGS,
    ActionInput,
    ActionResult,
    Concept,
    Format,
    Item,
    ItemType,
    normalize_concepts,
)
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


def as_concept_items(concepts: list[Concept]) -> list[Item]:
    concept_items = []
    for concept in concepts:
        concept_item = Item(
            type=ItemType.concept,
            title=concept,
            format=Format.markdown,
        )
        concept_items.append(concept_item)
    return concept_items


@kash_action(
    expected_args=ONE_OR_MORE_ARGS,
    precondition=is_markdown_list,
)
def save_concepts(input: ActionInput) -> ActionResult:
    """
    Creates a concept item for each value in a markdown list of concepts.
    Skips existing concepts and duplicates.
    """
    concepts = []
    for item in input.items:
        if not item.body:
            raise InvalidInput("Item must have a body")

        concepts.extend(concepts_from_bullet_points(item.body))

    result_items = as_concept_items(normalize_concepts(concepts))

    return ActionResult(result_items, skip_duplicates=True)
