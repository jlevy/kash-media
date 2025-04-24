from collections.abc import Callable

import pandas as pd
from funlog import tally_calls

from kash.config.logger import get_logger
from kash.embeddings.cosine import ArrayLike
from kash.embeddings.embeddings import Embeddings
from kash.embeddings.text_similarity import cosine_relatedness

log = get_logger(__name__)


def sort_by_length(values: list[str]) -> list[str]:
    return sorted(values, key=lambda x: (len(x), x))


@tally_calls(level="warning", min_total_runtime=5, if_slower_than=10)
def relate_texts_by_embedding(
    embeddings: Embeddings,
    relatedness_fn: Callable[[ArrayLike, ArrayLike], float] = cosine_relatedness,
) -> pd.DataFrame:
    log.message("Computing relatedness matrix of %d text embeddings…", len(embeddings.data))

    keys = [key for key, _, _ in embeddings.as_iterable()]
    relatedness_matrix = pd.DataFrame(index=keys, columns=keys)  # pyright: ignore

    for i, (key1, _, emb1) in enumerate(embeddings.as_iterable()):
        for j, (key2, _, emb2) in enumerate(embeddings.as_iterable()):
            if i <= j:
                score = relatedness_fn(emb1, emb2)
                relatedness_matrix.at[key1, key2] = score
                relatedness_matrix.at[key2, key1] = score

    # Fill diagonal (self-relatedness).
    for key in keys:
        relatedness_matrix.at[key, key] = 1.0

    return relatedness_matrix


def find_related_pairs(
    relatedness_matrix: pd.DataFrame, threshold: float = 0.9
) -> list[tuple[str, str, float]]:
    """
    Slow, brute-force implementation.
    """
    log.message(
        "Finding near duplicates among %s items (threshold %s)",
        relatedness_matrix.shape[0],
        threshold,
    )

    pairs: list[tuple[str, str, float]] = []
    keys = relatedness_matrix.index.tolist()

    for i, key1 in enumerate(keys):
        for j, key2 in enumerate(keys):
            if i < j:
                relatedness = relatedness_matrix.at[key1, key2]
                if relatedness >= threshold:
                    # Put shortest one first.
                    [short_key, long_key] = sort_by_length([key1, key2])
                    pairs.append((short_key, long_key, relatedness))

    # Sort with highest relatedness first.
    pairs.sort(key=lambda x: x[2], reverse=True)

    return pairs
