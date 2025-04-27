from kash.exec import kash_action
from kash.exec.preconditions import is_doc_resource
from kash.kits.media.docs.markitdown_custom_docx import CustomDocxConverter
from kash.model import Format, Item, ItemType
from kash.utils.errors import InvalidInput
from kash.workspaces.workspaces import current_ws


@kash_action(
    precondition=is_doc_resource,
    mcp_tool=True,
)
def to_md_markitdown(item: Item) -> Item:
    """
    Convert docs to markdown using MarkItDown, which wraps Mammoth and
    Markdownify.
    """
    from markitdown import MarkItDown

    if not item.store_path:
        raise InvalidInput(f"Missing store path for item: {item}")

    ws = current_ws()
    doc_path = ws.base_dir / item.store_path

    # Preserve superscript and subscripts, which are important for
    # Gemini Deep Research report docx files.
    # https://github.com/matthewwithanm/python-markdownify
    docx_converter = CustomDocxConverter(
        markdownify_options={
            "sup_symbol": "<sup>",
            "sub_symbol": "<sub>",
        }
    )
    mid = MarkItDown(enable_plugins=False)
    mid.register_converter(docx_converter)
    result = mid.convert(doc_path)
    markdown_content: str = result.markdown
    title: str = result.title or item.abbrev_title()

    output_item = item.derived_copy(
        type=ItemType.doc, format=Format.markdown, title=title, body=markdown_content
    )

    return output_item
