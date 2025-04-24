from chopdiff.docs import TextDoc
from chopdiff.transforms import WINDOW_2K_WORDTOKS, changes_whitespace

from kash.config.logger import get_logger
from kash.exec import SkipItem, kash_action, llm_transform_item
from kash.llm_utils import LLM, Message, MessageTemplate
from kash.model import Item, LLMOptions, Param

log = get_logger(__name__)


llm_options = LLMOptions(
    model=LLM.default_fast,
    diff_filter=changes_whitespace,
    windowing=WINDOW_2K_WORDTOKS,
    system_message=Message(
        """
        You are a careful and precise editor.
        You give exactly the results requested without additional commentary.
        """
    ),
    body_template=MessageTemplate(
        """
        Format this text according to these rules:

        - Break the following text into paragraphs so it is readable and organized.

        - Add a paragraph break whenever the topic changes.

        - Paragraphs can be short or up to several sentences long.

        - Do *not* change any words of the text. Add line breaks only.

        - Preserve all Markdown formatting.

        - ONLY GIVE THE FORMATTED TEXT, with no other commentary.

        Original text:

        {body}

        Formatted text:
        """
    ),
)


@kash_action(
    llm_options=llm_options,
    params=(
        Param(
            "max_sent_per_para",
            "Maximum number of sentences per paragraph.",
            type=int,
            default_value=7,
        ),
    ),
)
def break_into_paragraphs(item: Item, max_sent_per_para: int = 7) -> Item:
    """
    Reformat text as paragraphs. Preserves all text exactly except for whitespace changes.
    Does nothing if there are very few sentences.
    """
    if not item.body:
        raise SkipItem()

    # Check each paragraph's sentence count to see if we can skip this step altogether.
    doc = TextDoc.from_text(item.body)
    log.message("Doc size: %s", doc.size_summary())
    biggest_para = max(doc.paragraphs, key=lambda p: len(p.sentences))
    can_skip = len(biggest_para.sentences) <= max_sent_per_para

    log.message(
        "Checking if we need to break into paragraphs: "
        "biggest paragraph has %d sentences vs max of %d so %s",
        len(biggest_para.sentences),
        max_sent_per_para,
        "can skip" if can_skip else "must run",
    )
    if can_skip:
        raise SkipItem()

    # Finally, do the transform.
    result_item = llm_transform_item(item)
    return result_item
