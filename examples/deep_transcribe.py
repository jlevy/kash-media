from pathlib import Path
from typing import Tuple

import click

from kash.actions.core.strip_html import strip_html
from kash.actions.core.webpage_config import webpage_config
from kash.actions.core.webpage_generate import webpage_generate
from kash.exec import assemble_action_input
from kash.kits.media.actions.add_description import add_description
from kash.kits.media.actions.add_summary_bullets import add_summary_bullets
from kash.kits.media.actions.backfill_timestamps import backfill_timestamps
from kash.kits.media.actions.break_into_paragraphs import break_into_paragraphs
from kash.kits.media.actions.caption_paras import caption_paras
from kash.kits.media.actions.insert_frame_captures import insert_frame_captures
from kash.kits.media.actions.insert_section_headings import insert_section_headings
from kash.kits.media.actions.transcribe import transcribe
from kash.model import ActionInput, Item
from kash.workspaces import get_workspace


def basic_transcribe(item: Item) -> Item:
    # These are all simple actions, so take just accept and return one Item.
    transcribed = transcribe(item)

    stripped = strip_html(transcribed)

    paragraphs = break_into_paragraphs(stripped)

    clean_transcript = backfill_timestamps(paragraphs)

    return clean_transcript


def annotate_transcription(item: Item) -> Item:
    with_headings = insert_section_headings(item)

    with_captions = caption_paras(with_headings)

    with_summary = add_summary_bullets(with_captions)

    with_description = add_description(with_summary)

    md_final = insert_frame_captures(with_description)

    return md_final


def deep_transcribe(url: str, workspace_path: Path, rerun: bool) -> Tuple[Path, Path]:

    # Get or initialize a workspace directory.
    ws = get_workspace(workspace_path)

    input = assemble_action_input(ws, url)

    clean_transcript = basic_transcribe(input.items[0])

    annotated_transcript = annotate_transcription(clean_transcript)

    # These are regular actions that require ActionInput/ActionResult.
    config = webpage_config(ActionInput(items=[annotated_transcript]))

    html_final = webpage_generate(ActionInput(items=config.items))

    assert annotated_transcript.store_path
    assert html_final.items[0].store_path

    md_path = Path(annotated_transcript.store_path)
    html_path = Path(html_final.items[0].store_path)

    print("\n\nAll done!")
    print(f"Cleanly formatted Markdown/HTML is at: {md_path}")
    print(f"Browser-ready HTML is at: {html_path}")

    return md_path, html_path


@click.command()
@click.argument("url", type=click.STRING)
@click.option(
    "--workspace",
    type=click.STRING,
    help="The workspace directory to use for files, metadata, and cache",
    default=".",
)
@click.option(
    "--rerun",
    is_flag=True,
    help="Rerun actions even if the outputs already exist",
)
def cli_main(url: str, workspace: str, rerun: bool) -> None:
    """
    Take a video or audio URL (such as YouTube), download and cache it, and
    perform a "deep transcription" of it, including, full transcription,
    identifying speakers, adding sections, timestamps, and annotations,
    and inserting frame captures.
    """
    deep_transcribe(url, Path(workspace), rerun)


if __name__ == "__main__":
    cli_main()
