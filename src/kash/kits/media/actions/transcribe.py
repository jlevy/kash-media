from chopdiff.divs import parse_divs

import kash.kits.media.libs  # noqa: F401  # Ensure all media tools are available.
from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_audio_resource, is_url_item, is_video_resource
from kash.media_base.media_tools import cache_and_transcribe
from kash.model import FileExt, Format, Item, ItemType, common_params
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import as_file_url
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_action(
    name="transcribe",
    precondition=is_url_item | is_audio_resource | is_video_resource,
    params=common_params("language"),
    mcp_tool=True,
)
def transcribe(item: Item, language: str = "en") -> Item:
    """
    Download and transcribe audio from a podcast or video.
    """

    if item.url:
        url = item.url
    else:
        url = as_file_url(current_ws().base_dir / not_none(item.store_path))

    transcription = cache_and_transcribe(url, language=language)

    result_item = item.derived_copy(
        type=ItemType.doc,
        body=transcription,
        format=Format.html,  # Important to note this since we put in timestamp span tags.
        file_ext=FileExt.html,
        external_path=None,
    )

    log.message("Got transcription: %s", parse_divs(transcription).size_summary())

    return result_item
