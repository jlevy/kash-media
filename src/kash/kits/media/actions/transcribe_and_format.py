from kash.actions.core.strip_html import strip_html
from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_audio_resource, is_url_item, is_video_resource
from kash.kits.media.actions.backfill_timestamps import backfill_timestamps
from kash.kits.media.actions.break_into_paragraphs import break_into_paragraphs
from kash.kits.media.actions.identify_speakers import identify_speakers
from kash.kits.media.actions.transcribe import transcribe
from kash.model import Item
from kash.model.params_model import common_params

log = get_logger(__name__)


@kash_action(
    precondition=is_url_item | is_audio_resource | is_video_resource,
    params=common_params("language"),
    mcp_tool=True,
)
def transcribe_and_format(item: Item, language: str = "en") -> Item:
    """
    Same as `transcribe` plus attempt to
    identify the speakers, break text into paragraphs and if possible adding
    timestamps with links per paragraph.
    """
    transcribed_item = transcribe(item, language=language)

    with_speakers = identify_speakers(transcribed_item)

    stripped = strip_html(with_speakers)

    paragraphs = break_into_paragraphs(stripped)

    with_timestamps = backfill_timestamps(paragraphs)

    return with_timestamps
