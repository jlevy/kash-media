from dataclasses import dataclass

from typing_extensions import override

from kash.config.logger import get_logger

log = get_logger(__name__)

# Originally adapted from:
# https://cookbook.openai.com/examples/named_entity_recognition_to_enrich_text


@dataclass(frozen=True)
class ConceptLabel:
    label: str
    description: str

    @override
    def __str__(self) -> str:
        return f"{self.label}: {self.description}"


CONCEPT_LABELS = [
    ConceptLabel("person", "people, including real, historical, and fictional characters"),
    ConceptLabel("facility", "buildings, airports, highways, bridges"),
    ConceptLabel("company", "businesses and company names"),
    ConceptLabel("organization", "non-company groups, organizations, agencies, institutions"),
    ConceptLabel("city", "names of cities, towns, villages, etc."),
    ConceptLabel("country", "names of countries, states, provinces, etc."),
    ConceptLabel(
        "place",
        "names of regions any other geographic areas that are not countries, states, provinces "
        "(e.g. Europe, Scandinavia,  etc.) or other non-geopolitical locations, such as mountains, lakes, oceans, notable "
        "landmarks, etc. (e.g. Lake Michigan, Mount Everest, the Pyramids at Giza)",
    ),
    ConceptLabel(
        "event",
        "notable events, like scientific milestones, historical events "
        "(the Reformation, the 9/11 attacks)",
    ),
    ConceptLabel(
        "product",
        "a physical product, including vehicles, foods, apparal, appliances, toys, "
        "devices, etc. (excluding software)",
    ),
    ConceptLabel(
        "software",
        "software or similar intangible products, including apps, games, and open source "
        "(e.g. Microsoft Excel, GitHub repositories)",
    ),
    ConceptLabel("book", "books"),
    ConceptLabel("academic work", "academic papers, articles, or proceedings"),
    ConceptLabel("article", "articles, news stories, or other published, written works"),
    ConceptLabel("post", "blog posts, social media posts, tweets, or other online content"),
    ConceptLabel("video", "movies, TV shows, or other video content"),
    ConceptLabel("audio", "songs, podcasts, or other audio content"),
    ConceptLabel("musical work", "musical works or songs"),
    ConceptLabel("artwork", "other artwork in any medium"),
    ConceptLabel("law", "named laws, acts, or legislations"),
    ConceptLabel(
        "language",
        "any named language (e.g. English, French, Chinese, etc.) ",
    ),
    ConceptLabel(
        "culture",
        "any religious or cultural group (e.g. Catholicism, Canadians, Hmong, South Asian, LGBTQ)",
    ),
    ConceptLabel(
        "activity", "any kind of activity or game or event (e.g. soccer, chess, deep knee bends)"
    ),
    # ConceptLabel("time", "time units smaller than a day", is_quantitative=True),
    # ConceptLabel("monetary", "monetary values, including number and unit", is_quantitative=True),
    # ConceptLabel(
    #     "quantity",
    #     "numeric measurements, e.g., weight or distance, including number and "
    #     "unit ('25km', 'five ounces')",
    #     is_quantitative=True,
    # ),
    # ConceptLabel(
    #     "number",
    #     "numeric values, including percentages (e.g., 'twenty percent', '18%')",
    #     is_quantitative=True,
    # ),
    # ConceptLabel(
    #     "date",
    #     "absolute or relative dates or periods (e.g. 1995, 2020-01-01, 2020 BC)",
    #     is_quantitative=True,
    # ),
    # ConceptLabel(
    #     "theory",
    #     "specific academic theories, philosophies, theorems (e.g. the chain rule, "
    #     "Occam's Razor, existentialism)",
    # ),
    # ConceptLabel(
    #     "concept",
    #     "any specific well-defined concept as it might appear in the index of a book "
    #     "(e.g. dieting, furniture, the stock market, social media) but DO NOT include very general "
    #     "concepts like people, power, problem, solution, a number, etc.",
    # ),
]
