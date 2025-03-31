from chopdiff.html import html_find_tag

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_html_body, has_text_body
from kash.model import Item, ItemType
from kash.utils.common.string_replace import replace_multiple
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


@kash_action(
    precondition=has_html_body | has_text_body,
)
def remove_speaker_labels(item: Item) -> Item:
    """
    Remove speaker labels (<span data-speaker-id=...>...</span>) from the transcript.
    Handy when the transcription has added them erroneously.
    """
    if not item.body:
        raise InvalidInput("Item must have a body")

    # Find all <span data-speaker-id=...>...</span> elements.
    matches = html_find_tag(item.body, tag_name="span", attr_name="data-speaker-id")

    # Prepare replacements to remove these elements.
    replacements = []
    for match in matches:
        replacements.append((match.start_offset, match.end_offset, ""))

    # Remove the speaker labels from the body.
    new_body = replace_multiple(item.body, replacements)

    # Create a new item with the cleaned body with same doc type and format.
    output_item = item.derived_copy(type=ItemType.doc, body=new_body)

    return output_item
