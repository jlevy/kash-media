from kash.exec import kash_action
from kash.exec.preconditions import is_markdown
from kash.kits.media.docs.markdown_footnotes import convert_endnotes_to_footnotes
from kash.model import Format, Item, ItemType


@kash_action(precondition=is_markdown)
def endnotes_to_footnotes(item: Item) -> Item:
    """
    Remove endnotes from a Markdown document and replace them with footnotes.
    Looks for <sup>n</sup> tags and and an enumerated list of notes and replaces
    the list items with Markdown footnotes.
    """
    if not item.body:
        raise ValueError("Item has no body")

    new_body = convert_endnotes_to_footnotes(item.body, strict=False)

    return item.derived_copy(
        type=ItemType.doc,
        format=Format.markdown,
        body=new_body,
    )
