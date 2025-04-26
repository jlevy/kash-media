from kash.exec import kash_action
from kash.exec.preconditions import is_doc_resource
from kash.model import Format, Item, ItemType
from kash.utils.errors import InvalidInput
from kash.workspaces.workspaces import current_ws


@kash_action(
    precondition=is_doc_resource,
    mcp_tool=True,
)
def to_md_markitdown(item: Item) -> Item:
    """
    Convert docs to markdown using Microsoft MarkItDown.
    """
    from markitdown import MarkItDown

    if not item.store_path:
        raise InvalidInput(f"Missing store path for item: {item}")

    ws = current_ws()
    doc_path = ws.base_dir / item.store_path

    mid = MarkItDown(enable_plugins=False)
    result = mid.convert(doc_path)
    markdown_content: str = result.markdown
    title: str = result.title or item.abbrev_title()

    output_item = item.derived_copy(
        type=ItemType.doc, format=Format.markdown, title=title, body=markdown_content
    )

    return output_item
