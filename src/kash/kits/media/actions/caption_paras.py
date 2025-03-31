from chopdiff.divs import div
from chopdiff.docs import Paragraph, TextDoc, TextUnit

from kash.config.logger import get_logger
from kash.exec import kash_action, kash_precondition
from kash.exec.llm_transforms import llm_transform_str
from kash.llm_utils import Message, MessageTemplate
from kash.model import Format, Item, ItemType, LLMOptions
from kash.utils.common.task_stack import task_stack
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


llm_options = LLMOptions(
    system_message=Message(
        """
        You are a careful and precise editor.
        You give exactly the results requested without additional commentary.
        """
    ),
    body_template=MessageTemplate(
        """
        Please describe what is said in the following one or two paragraphs, as a 
        summary or caption for the content. Rules:

        - Mention only the most important points. Include all the key topics discussed.
        
        - Keep the caption short! Use one or two short, complete sentences. It must be significantly
            shorter than the input text.
        
        - Write in clean and and direct language.

        - Do not mention the text or the author. Simply state the points as presented.

        - If the content contains other promotional material or only references information such as
            about what will be discussed later, ignore it.

        - DO NOT INCLUDE any other commentary.

        - If the input is very short or so unclear you can't summarize it, simply output
            "(No results)".

        - If the input is in a language other than English, output the caption in the same language.

        Sample input text:

        I think push ups are one of the most underrated exercises out there and they're also one of
        the exercises that is most frequently performed with poor technique.
        And I think this is because a lot of people think it's just an easy exercise and they adopt
        a form that allows them to achieve a rep count that they would expect from an easy exercise,
        but all that ends up happening is they they do a bunch of poor quality repetitions in order
        to get a high rep count. So I don't think push ups are particularly easy when they're done well
        and they're really effective for building just general fitness and muscle in the upper body
        if you do them properly. So here's how you get the most out of them.

        Sample output text:

        Push ups are an underrated exercise. They are not easy to do well so are often done poorly.

        Input text:

        {body}

        Output text:
        """
    ),
)


PARA = "para"
ANNOTATED_PARA = "annotated-para"
PARA_CAPTION = "para-caption"


@kash_precondition
def has_annotated_paras(item: Item) -> bool:
    """
    Useful to check if an item has already been annotated with captions.
    """
    return bool(item.body and item.body.find(f'<p class="{ANNOTATED_PARA}">') != -1)


def process_para(llm_options: LLMOptions, para: Paragraph) -> str:
    caption_div = None

    para_str = para.reassemble()
    # Only caption actual paragraphs with enough words.
    if not para.is_markup() and not para.is_header() and para.size(TextUnit.words) > 40:
        log.message("Captioning paragraph (%s words)", para.size(TextUnit.words))
        llm_response = llm_transform_str(llm_options, para_str)
        caption_div = div(PARA_CAPTION, llm_response)
        new_div = div(ANNOTATED_PARA, caption_div, div(PARA, para_str))
    else:
        log.message(
            "Skipping captioning very short paragraph (%s words)", para.size(TextUnit.words)
        )
        new_div = para_str
    return new_div


@kash_action(llm_options=llm_options)
def caption_paras(item: Item) -> Item:
    """
    Caption each paragraph in the text with a very short summary, wrapping the original
    and the caption in simple divs.
    """
    if not item.body:
        raise InvalidInput(f"Item must have a body: {item}")

    doc = TextDoc.from_text(item.body)
    output = []
    with task_stack().context("caption_paras", doc.size(TextUnit.paragraphs), "para") as ts:
        for para in doc.paragraphs:
            if para.size(TextUnit.words) > 0:
                output.append(process_para(llm_options, para))
            ts.next()

    final_output = "\n\n".join(output)
    result_item = item.derived_copy(type=ItemType.doc, body=final_output, format=Format.md_html)

    return result_item
