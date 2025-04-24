from kash.model.concept_model import Concept, normalize_concepts
from kash.text_handling.markdown_utils import extract_bullet_points


def concepts_from_bullet_points(
    markdown_text: str, sort_dedup: bool = True, capitalize: bool = True
) -> list[Concept]:
    """
    Parse, normalize, capitalize concepts as a Markdown bullet list. If sort_dedup is True,
    sort and remove exact duplicates.
    """
    concepts: list[str] = extract_bullet_points(markdown_text)  # noqa: F821
    return normalize_concepts(concepts, sort_dedup, capitalize)
