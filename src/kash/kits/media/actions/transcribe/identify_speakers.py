import json
from textwrap import dedent

from strif import StringTemplate, replace_multiple

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_html_body, has_simple_text_body
from kash.kits.media.video.speaker_labels import find_speaker_labels
from kash.llm_utils import LLM, LLMName, Message, MessageTemplate
from kash.llm_utils.fuzzy_parsing import fuzzy_parse_json
from kash.llm_utils.llm_completion import llm_template_completion
from kash.media_base.timestamp_citations import html_speaker_id_span
from kash.model import Item, ItemType
from kash.model.params_model import common_params
from kash.utils.errors import ApiResultError, InvalidInput

log = get_logger(__name__)


@kash_action(
    precondition=has_simple_text_body | has_html_body,
    params=common_params("model"),
)
def identify_speakers(item: Item, model: LLMName = LLM.default_fast) -> Item:
    """
    Identify speakers in a transcript and replace placeholders with their names.
    """
    if not item.body:
        raise InvalidInput("Item must have a body")

    # Find all speaker labels and their offsets
    speaker_labels = find_speaker_labels(item.body)
    if not speaker_labels:
        log.warning("This document has no speaker labels! Skipping this action.")
        return item  # No changes needed.

    # Prepare the system message and template for LLM.
    system_message = Message("You are an assistant that identifies speakers in transcripts.")
    message_template = StringTemplate(
        """
        The transcript below includes speakers identified by IDs like 'SPEAKER 0' or 'SPEAKER 1'.
        Based on the info below and the transcript, provide a mapping from speaker IDs to
        actual speaker names.

        The mapping should be in JSON format.
        If you are not sure from the content, leave the names as is and only fill in the
        known names. Examples:
        {json_examples}

        First, here is the available info on the original recording or video:

        Title: {title}
        Description: {description}

        Transcript:

        """,
        allowed_fields=["title", "description", "json_examples"],
    )

    json_examples = dedent(
        """
        Example 1: {{"0": "Alice", "1": "Bob"}}

        Example 2: {{"0": "Alice", "1": "SPEAKER 1"}}

        Example 3: {{"0": "SPEAKER 0", "1": "SPEAKER 1"}}
        """
    )

    message = message_template.format(
        title=item.title, description=item.description, json_examples=json_examples
    )

    # Perform LLM completion to get the speaker mapping.
    mapping_str = llm_template_completion(
        model=model,
        system_message=system_message,
        input=item.body,
        body_template=MessageTemplate(message + "\n\n" + "{body}"),
    ).content

    # Parse the mapping.
    try:
        speaker_mapping = fuzzy_parse_json(mapping_str)
        if not speaker_mapping:
            log.error("Could not parse speaker mapping: %s", mapping_str)
            raise ApiResultError("Could not parse speaker mapping")
        log.message("Identified speakers from transcript: %s", speaker_mapping)
    except json.JSONDecodeError as e:
        raise ApiResultError(f"Failed to parse speaker mapping from LLM output: {e}")

    # Prepare replacements.
    replacements = []
    for match in speaker_labels:
        speaker_id = match.attribute_value
        if not speaker_id:
            raise InvalidInput(f"Speaker id not found: {match}")
        new_speaker_name = speaker_mapping.get(speaker_id, f"SPEAKER {speaker_id}")
        # Prepare replacement text.
        new_span = html_speaker_id_span(f"**{new_speaker_name}:**", speaker_id)
        replacements.append((match.start_offset, match.end_offset, new_span))

    # Perform replacements.
    updated_body = replace_multiple(item.body, replacements)

    result_item = item.derived_copy(type=ItemType.doc, body=updated_body)
    return result_item


## Tests


def test_identify_speakers_forwards_selected_model():
    from inspect import unwrap
    from types import SimpleNamespace
    from unittest.mock import patch

    model = LLMName("gpt-5.6-luna")
    item = Item(
        type=ItemType.doc,
        title="Alice interviews Bob",
        body=(
            '<span class="speaker-label" data-speaker-id="0">SPEAKER 0:</span> Hello. '
            '<span class="speaker-label" data-speaker-id="1">SPEAKER 1:</span> Hi.'
        ),
    )

    with patch(
        "kash.kits.media.actions.transcribe.identify_speakers.llm_template_completion",
        return_value=SimpleNamespace(content='{"0": "Alice", "1": "Bob"}'),
    ) as completion:
        result = unwrap(identify_speakers)(item, model=model)

    assert result.body
    assert "Alice" in result.body
    assert "Bob" in result.body
    assert completion.call_args.kwargs["model"] == model
