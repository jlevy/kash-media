from chopdiff.transforms import WINDOW_128_PARA, adds_headings

from kash.config.logger import get_logger
from kash.exec import kash_action, llm_transform_item
from kash.llm_utils import LLM, Message, MessageTemplate
from kash.model import Item, LLMOptions

log = get_logger(__name__)


llm_options = LLMOptions(
    model=LLM.default_fast,
    diff_filter=adds_headings,
    windowing=WINDOW_128_PARA,
    system_message=Message(
        """
        You are a careful and precise editor.
        You give exactly the results requested without additional commentary.
        """
    ),
    body_template=MessageTemplate(
        """
        Insert headings into the following text using `<h2>` tags. 

        - Add a heading every time topics change, typically after 3-6 paragraphs, but follow your
          best judgement in terms of when the change in topic occurs.

        - Each heading should describe what is covered by the paragraphs that follow.

        - DO NOT change any text other than to add headings, each on its own line, in
          between the paragraphs of the text.
                        
        - Section headings should be concise and specific. For example, use
          "Importance of Sleep" and not just "Sleep", or "Reflections on Johanna's Early Childhood" and
          not just "Childhood".
          
        - Do NOT give any introductory response at the beginning, such as "Here is the text
          with headings added".

        - If the input is short, you can add a single heading at the beginning.

        - If the input is very short or unclear, output the text exactly, without adding any headings.

        - If the input is in a language other than English, output the text in the same language.

        Input text:

        {body}

        Output text (identical to input, but with headings added):
        """
    ),
)


@kash_action(llm_options=llm_options)
def insert_section_headings(item: Item) -> Item:
    """
    Insert headings into a text as <h2> tags.
    """
    return llm_transform_item(item)
