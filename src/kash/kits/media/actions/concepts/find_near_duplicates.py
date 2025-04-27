from chopdiff.util import lemmatized_equal

from kash.config.logger import get_logger
from kash.embeddings.embeddings import Embeddings
from kash.exec import kash_action
from kash.exec.preconditions import is_concept, is_text_doc
from kash.kits.media.concepts.concept_relations import (
    find_related_pairs,
    relate_texts_by_embedding,
)
from kash.model import TWO_OR_MORE_ARGS, ActionInput, ActionResult, PathOp, PathOpType, StorePath
from kash.shell.output.shell_output import PrintHooks, cprint, print_h3
from kash.text_handling.markdown_utils import as_bullet_points
from kash.utils.common.type_utils import not_none

log = get_logger(__name__)


@kash_action(
    expected_args=TWO_OR_MORE_ARGS,
    precondition=is_concept | is_text_doc,
)
def find_near_duplicates(input: ActionInput) -> ActionResult:
    """
    Look at input items and find near duplicate items using text embeddings, based on title or body.
    """
    keyvals = [(not_none(item.store_path), item.full_text()) for item in input.items]
    item_map = {item.store_path: item for item in input.items}

    report_threshold = 0.65
    archive_threshold = 0.85

    embeddings = Embeddings.embed(keyvals)
    relatedness_matrix = relate_texts_by_embedding(embeddings)
    near_duplicates = find_related_pairs(relatedness_matrix, threshold=report_threshold)

    # Give a report on most related items.
    report_lines = []
    duplicate_paths = []
    for key1, key2, score in near_duplicates:
        item1 = item_map[key1]
        item2 = item_map[key2]
        lem_eq = lemmatized_equal(item1.full_text(), item2.full_text())
        line = f"{item1.title} <-> {item2.title} ({score:.3f}) {lem_eq}"
        report_lines.append(line)

        if score >= archive_threshold or lem_eq:
            duplicate_paths.append(key1)  # key1 will be the shorter one.
    report = as_bullet_points(report_lines)

    print_h3("Near Duplicates")
    cprint(f"Most-related items (score >= {report_threshold}):")
    PrintHooks.spacer()
    if report:
        cprint("%s", report)
    else:
        cprint("No near duplicates found!")
    PrintHooks.spacer()

    # TODO: Handle concepts that subsume other concepts, e.g. find ones like this even
    # though the similarity score is low:
    # - AGI <-> AGI (Artificial General Intelligence) (0.640)

    return ActionResult(
        [],
        path_ops=[
            PathOp(store_path=StorePath(path), op=PathOpType.select) for path in duplicate_paths
        ],
    )
