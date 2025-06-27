from kash.exec import kash_action
from kash.exec.preconditions import is_audio_resource, is_url_resource, is_video_resource
from kash.kits.docs.actions.text.add_description import add_description
from kash.kits.docs.actions.text.add_summary_bullets import add_summary_bullets
from kash.kits.docs.actions.text.insert_section_headings import insert_section_headings
from kash.kits.docs.actions.text.research_paras import research_paras
from kash.kits.media.actions.transcribe.insert_frame_captures import insert_frame_captures
from kash.kits.media.actions.transcribe.transcribe_format import transcribe_format
from kash.model import Item, common_params


@kash_action(
    precondition=is_url_resource | is_audio_resource | is_video_resource,
    params=common_params("language"),
    mcp_tool=True,
)
def transcribe_annotate(item: Item, language: str = "en") -> Item:
    """
    Do everything `transcribe_format` does plus adding sections,
    paragraph annotations, frame captures (avoiding duplicative frames),
    a bulleted summary, and a description at the top.
    """
    formatted = transcribe_format(item, language=language)

    with_headings = insert_section_headings(formatted)

    with_research = research_paras(with_headings)

    # with_para_summaries = summarize_paras(with_research)

    with_summary = add_summary_bullets(with_research)

    with_description = add_description(with_summary)

    with_frames = insert_frame_captures(with_description)

    return with_frames
