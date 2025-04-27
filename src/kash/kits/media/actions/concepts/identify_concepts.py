from chopdiff.transforms import WINDOW_2_PARA

from kash.config.logger import get_logger
from kash.exec import kash_action, llm_transform_item
from kash.kits.media.concepts.concept_labels import CONCEPT_LABELS
from kash.kits.media.concepts.concept_utils import concepts_from_bullet_points
from kash.llm_utils import LLM, LLMName, Message, MessageTemplate
from kash.llm_utils.fuzzy_parsing import is_no_results
from kash.model import Item, LLMOptions, TitleTemplate, common_params
from kash.text_handling.markdown_utils import as_bullet_points
from kash.utils.errors import InvalidOutput

log = get_logger(__name__)

# Originally adapted from:
# https://cookbook.openai.com/examples/named_entity_recognition_to_enrich_text

labels_str = "\n".join(str(label) for label in CONCEPT_LABELS)

llm_options = LLMOptions(
    model=LLM.default_standard,
    windowing=WINDOW_2_PARA,
    system_message=Message(
        f"""
        You are a careful editor annotating concepts as you would to produce a high-quality
        index in a book. You are given a text of one or more paragraphs and you must output a
        list of named entities or concepts assigned into one of the categories below.

        Output *must* be in bulleted Markdown list format, with no other text or formatting,
        exactly in the format it originally appears (including any capitalization or inflections)
        with the entity type in parentheses.

        For concepts, DO NOT include very abstract and broad concepts.

        For example DO NOT include these as they are too general:
        human (concept), power (concept), technical problem (concept),
        solutions (concept), state (concept), success (concept), three (number),
        technology (concept), nuance (concept), information (concept), analogy (concept),
        green (concept), fuzziness (concept)

        DO include more specific or concrete concepts. DO include:
        state management (concept), refactoring (concept),
        dampening coefficient (concept), brain (concept),
        depression (concept), pit of despair (concept), programming (activity),
        graph traversal algorithms (theory), decision theory (theory)

        If no entities are found, return the string: "(No results)"

        Each item should be labeled for clarity and to disambiguate it, with one of
        these labels:
        {labels_str}.
        """
    ),
    body_template=MessageTemplate(
        """
        TASK EXAMPLE 1:

        Input text:

        In Germany, in 1440, goldsmith Johannes Gutenberg invented the movable-type printing press.
        His work led to an information revolution and the unprecedented mass-spread of literature
        throughout Europe. Modelled on the design of the existing screw presses, a single
        Renaissance movable-type printing press could produce up to 3,600 pages per workday.
        Within a single generation, printers in Mainz, Venice, Nuremberg, and Paris were
        turning out incunabula—early printed books—on grammar, law, medicine, and, crucially,
        the Bible in both Latin and the emerging vernaculars.

        The via moderna in philosophy: Nominalist ideas—William of Ockham’s insistence on
        empirical particulars over abstract universals—found a wider audience, nudging
        thought toward observation and away from scholastic syllogism.

        Concepts:

        - Germany (country)
        - 1440 (date)
        - Johannes Gutenberg (person)
        - movable-type printing press (product)
        - literature (concept)
        - Europe (region)
        - Renaissance (event)
        - 3,600 pages (quantity)
        - Mainz (city)
        - Venice (city)
        - Nuremberg (city)
        - Paris (city)
        - incunabula (concept)
        - grammar (concept)
        - law (concept)
        - medicine (concept)
        - The Bible (book)
        - Latin (culture)
        - vernaculars (culture)
        - via moderna (concept)
        - Nominalist ideas (theory)
        - William of Ockham (person)
        - scholastic syllogism (concept)


        TASK EXAMPLE 2:

        Input text:

        How are you doing?

        Concepts:

        (no results)

        NEW TASK:

        Input text:

        {body}

        Concepts:
        """
    ),
)


@kash_action(
    llm_options=llm_options,
    params=common_params("model"),
    title_template=TitleTemplate("Concepts from {title}"),
)
def identify_concepts(item: Item, model: LLMName = LLM.default_standard) -> Item:
    """
    Identify concepts or named entities in a text, returning a bulleted Markdown list of
    concepts, labeled by type.
    """
    result_item = llm_transform_item(item, model=model)

    if is_no_results(result_item.body or ""):
        raise InvalidOutput("No concepts found")

    result_item.body = as_bullet_points(concepts_from_bullet_points(result_item.body or ""))

    return result_item
