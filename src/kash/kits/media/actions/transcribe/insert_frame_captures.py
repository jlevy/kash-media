from chopdiff.divs import parse_divs
from chopdiff.docs import search_tokens
from chopdiff.html import TimestampExtractor, html_img, md_para
from strif import Insertion, insert_multiple

from kash.config.logger import get_logger
from kash.exec import kash_action, kash_precondition
from kash.exec.preconditions import has_simple_text_body, has_timestamps
from kash.kits.media.video.image_similarity import filter_similar_frames
from kash.kits.media.video.video_frames import capture_frames
from kash.model import Format, Item, ItemType, Param
from kash.utils.common.format_utils import fmt_loc
from kash.utils.common.url import as_file_url
from kash.utils.errors import ContentError, InvalidInput
from kash.utils.file_utils.file_formats_model import MediaType
from kash.web_content.file_cache_utils import cache_file, cache_resource
from kash.workspaces import current_ws
from kash.workspaces.source_items import find_upstream_resource

log = get_logger(__name__)


FRAME_CAPTURE = "frame-capture"
"""Class name for a frame capture from a video."""


@kash_precondition
def has_frame_captures(item: Item) -> bool:
    return bool(item.body and item.body.find(f'<img class="{FRAME_CAPTURE}">') != -1)


@kash_action(
    precondition=has_simple_text_body & has_timestamps & ~has_frame_captures,
    params=(
        Param(
            "threshold",
            "The similarity threshold for filtering consecutive frames.",
            type=float,
            default_value=0.6,
        ),
    ),
)
def insert_frame_captures(item: Item, threshold: float = 0.6) -> Item:
    """
    Look for timestamped video links and insert frame captures after each one.
    """
    if not item.body:
        raise InvalidInput("Item has no body")

    # Find the original video resource.
    orig_resource = find_upstream_resource(item)
    paths = cache_resource(orig_resource)
    if MediaType.video not in paths:
        raise InvalidInput(f"Item has no video: {item}")
    video_path = paths[MediaType.video]

    # Extract all timestamps.
    extractor = TimestampExtractor(item.body)
    timestamp_matches = list(extractor.extract_all())

    log.message(
        f"Found {len(timestamp_matches)} timestamps in the document, {parse_divs(item.body).size_summary()}."
    )

    # Extract frame captures, and put them in the workspace's assets directory.
    target_dir = current_ws().assets_dir
    timestamps = [timestamp for timestamp, _index, _offset in timestamp_matches]
    frame_paths = capture_frames(video_path, timestamps, target_dir, prefix=item.slug_name())

    # Save images in file cache for later as well.
    for frame_path in frame_paths:
        cache_file(frame_path)
    log.message(f"Saved {len(frame_paths)} frame captures to cache.")

    # Filter out similar consecutive frames.
    unique_indices = filter_similar_frames(frame_paths, threshold)
    unique_frame_paths = [frame_paths[i] for i in unique_indices]
    unique_matches = [timestamp_matches[i] for i in unique_indices]

    log.message(
        f"Filtered out {len(frame_paths) - len(unique_frame_paths)}/{len(frame_paths)} similar frames."
    )
    log.message(
        f"Extracted {len(unique_frame_paths)} unique frame captures to: {fmt_loc(target_dir)}"
    )

    # Create a set of indices that were kept.
    kept_indices = set(unique_indices)

    # Prepare insertions.
    log.message(
        "Inserting %s frame captures, have %s wordtoks",
        len(unique_matches),
        len(extractor.offsets),
    )
    insertions: list[Insertion] = []
    for i, (timestamp, index, offset) in enumerate(timestamp_matches):
        # Only process timestamps whose frames weren't filtered out
        if i not in kept_indices:
            continue

        try:
            insert_index = (
                search_tokens(extractor.wordtoks)
                .at(index)
                .seek_forward(["</span>"])
                .next()
                .get_index()
            )
        except KeyError:
            raise ContentError(
                f"No matching tag close starting at {offset}: {extractor.wordtoks[offset:]}"
            )

        new_offset = extractor.offsets[insert_index]
        frame_path = frame_paths[i]
        insertions.append(
            (
                new_offset,
                md_para(
                    html_img(
                        as_file_url(frame_path),  # TODO: Serve these.
                        f"Frame at {timestamp} seconds",
                        class_name=FRAME_CAPTURE,
                    )
                ),
            )
        )

    # Insert img tags into the document.
    output_text = insert_multiple(item.body, insertions)

    # Create output item.
    output_item = item.derived_copy(type=ItemType.doc, format=Format.md_html)
    output_item.body = output_text

    return output_item
