from chopdiff.divs import parse_divs

import kash.kits.docs.doc_formats  # noqa: F401  # Ensure all media tools are available.
from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_audio_resource, is_url_resource, is_video_resource
from kash.kits.media.transcription_context import get_transcription_metadata, parse_key_terms
from kash.media_base.media_tools import cache_and_transcribe
from kash.media_base.transcription_settings import TranscriptionSettings
from kash.model import FileExt, Format, Item, ItemType, Param, common_params
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import Url, as_file_url
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_action(
    precondition=is_url_resource | is_audio_resource | is_video_resource,
    params=common_params("language")
    + (
        Param(
            "transcription_model",
            "Speech-to-text model used by the transcription provider.",
            type=str,
            default_value="nova-3",
        ),
        Param(
            "diarize_model",
            "Speaker diarization model used by the transcription provider.",
            type=str,
            default_value="latest",
        ),
        Param(
            "key_terms",
            "Newline-separated terms Deepgram should recognize accurately.",
            type=str,
            default_value="",
        ),
    ),
    mcp_tool=True,
)
def transcribe(
    item: Item,
    language: str = "en",
    transcription_model: str = "nova-3",
    diarize_model: str = "latest",
    key_terms: str = "",
) -> Item:
    """
    Download and transcribe audio from a podcast or video and return raw text,
    including timestamps if available (as HTML `<span>` tags), also caching
    video, audio, and transcript as local files.
    """

    if item.url:
        url = item.url
    else:
        url = as_file_url(current_ws().base_dir / not_none(item.store_path))

    metadata = get_transcription_metadata(item)
    all_key_terms: list[str] = []
    for term in [*metadata.get("key_terms", []), *parse_key_terms(key_terms)]:
        if term not in all_key_terms:
            all_key_terms.append(term)
    settings = TranscriptionSettings.create(
        language=language,
        model=transcription_model,
        diarize_model=diarize_model,
        key_terms=all_key_terms,
    )
    transcription = cache_and_transcribe(url, settings=settings)

    result_item = item.derived_copy(
        type=ItemType.doc,
        body=transcription,
        format=Format.html,  # Important to note this since we put in timestamp span tags.
        file_ext=FileExt.html,
        external_path=None,
    )

    log.message("Got transcription: %s", parse_divs(transcription).size_summary())

    return result_item


## Tests


def test_transcribe_forwards_item_key_terms() -> None:
    from inspect import unwrap
    from unittest.mock import patch

    item = Item(
        type=ItemType.resource,
        format=Format.url,
        url=Url("https://example.com/interview"),
        extra={"transcription": {"key_terms": ["Alice Chen", "SignalFlow"]}},
    )
    transcription = '<span data-timestamp="0.0">Hello.</span>'

    with patch(
        "kash.kits.media.actions.transcribe.transcribe.cache_and_transcribe",
        return_value=transcription,
    ) as transcribe_audio:
        result = unwrap(transcribe)(
            item,
            language="multi",
            key_terms="SignalFlow\nNova Prime",
        )

    settings = transcribe_audio.call_args.kwargs["settings"]
    assert settings.language == "multi"
    assert settings.model == "nova-3"
    assert settings.diarize_model == "latest"
    assert settings.key_terms == ("Alice Chen", "SignalFlow", "Nova Prime")
    assert result.extra == item.extra
