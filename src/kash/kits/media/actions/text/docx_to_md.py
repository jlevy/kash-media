from kash.exec import kash_action
from kash.exec.preconditions import is_docx_resource
from kash.kits.media.docs import docx_convert
from kash.model import Format, Item, ItemType


@kash_action(precondition=is_docx_resource, mcp_tool=True)
def docx_to_md(item: Item) -> Item:
    """
    Convert a docx file to clean Markdown, hopefully in good enough shape
    to publish. Uses MarkItDown/Mammoth/Markdownify and a few additional
    cleanups.

    This works well to convert docx files from Gemini Deep Research
    output: click to export a report to Google Docs, then select `File >
    Download > Microsoft Word (.docx)`.
    """

    result = docx_convert.docx_to_md(item.absolute_path())

    return item.derived_copy(
        type=ItemType.doc,
        format=Format.markdown,
        title=result.title or item.abbrev_title(),
        body=result.markdown,
    )
