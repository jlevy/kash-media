from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_audio_resource, is_url_item, is_video_resource
from kash.kits.media.actions.add_description import add_description
from kash.kits.media.actions.add_summary_bullets import add_summary_bullets
from kash.kits.media.actions.caption_paras import caption_paras
from kash.kits.media.actions.insert_frame_captures import insert_frame_captures
from kash.kits.media.actions.insert_section_headings import insert_section_headings
from kash.kits.media.actions.transcribe_and_format import transcribe_and_format
from kash.model import Item, common_params

log = get_logger(__name__)


@kash_action(
    precondition=is_url_item | is_audio_resource | is_video_resource,
    params=common_params("language"),
    mcp_tool=True,
)
def transcribe_and_annotate(item: Item, language: str = "en") -> Item:
    """
    Do everything `transcribe_and_format` does plus adding sections,
    paragraph annotations, frame captures (avoiding duplicative frames),
    a bulleted summary, and a description at the top.
    """
    formatted = transcribe_and_format(item, language=language)

    with_headings = insert_section_headings(formatted)

    with_captions = caption_paras(with_headings)

    with_summary = add_summary_bullets(with_captions)

    with_description = add_description(with_summary)

    with_frames = insert_frame_captures(with_description)

    return with_frames
