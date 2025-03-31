from kash.exec import kash_action, llm_transform_item
from kash.llm_utils import Message, MessageTemplate
from kash.model import Item, LLMOptions, TitleTemplate

llm_options = LLMOptions(
    system_message=Message(
        """
        You are a careful and precise editor.
        You give exactly the results requested without additional commentary.
        """
    ),
    # TODO: Get a scene context/description from the resource and add it to this template.
    # Is this a book/article/transcript/lecture/interview/etc? Who was involved? When was it?
    # Create a question template and have this filled in.
    body_template=MessageTemplate(
        """
        Give a brief description of the entire text below, as a summary of two or three sentences.
        Write it concisely and clearly, in a form suitable for a short description of a web page
        or article.

        - Use simple and precise language.

        - Simply state the facts or claims without referencing the text or the author. For example, if the
          text is about cheese being nutritious, you can say "Cheese is nutritious." But do NOT
          say "The author says cheese is nutritious" or "According to the text, cheese is nutritious."

        - If the content is missing so brief that it can't be described, simply say "(No description.)"

        - If the input is in a language other than English, output the description in the same language.

        Original text:

        {body}

        Brief description of the text:
        """
    ),
)


@kash_action(llm_options=llm_options, title_template=TitleTemplate("Summary of {title}"))
def describe_briefly(item: Item) -> Item:
    """
    Write a brief description of a text, in at most three sentences.
    """
    return llm_transform_item(item)
