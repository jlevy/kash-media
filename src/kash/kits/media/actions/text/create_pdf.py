from os.path import join

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_html_body, has_text_body
from kash.kits.media.libs.pdf_output import html_to_pdf
from kash.llm_utils.clean_headings import clean_heading
from kash.model import FileExt, Format, Item, ItemType
from kash.utils.common.format_utils import fmt_loc
from kash.utils.errors import InvalidInput
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_action(
    precondition=has_text_body | has_html_body,
    mcp_tool=True,
)
def create_pdf(item: Item) -> Item:
    """
    Create a PDF from text or Markdown.
    """
    if not item.body:
        raise InvalidInput(f"Item must have a body: {item}")

    pdf_item = item.derived_copy(type=ItemType.export, format=Format.pdf, file_ext=FileExt.pdf)
    pdf_path, _found, _old_pdf_path = current_ws().store_path_for(pdf_item)
    log.message("Will save PDF to: %s", fmt_loc(pdf_path))
    base_dir = current_ws().base_dir
    full_pdf_path = join(base_dir, pdf_path)

    clean_title = clean_heading(item.abbrev_title())

    # Convert to HTML if necessary.
    if item.format == Format.html:
        content_html = f"""
            <h1>{clean_title}</h1>
            {item.body_text()}
            """
    else:
        content_html = f"""
            <h1>{clean_title}</h1>
            {item.body_as_html()}
            """

    # Add directly to the store.
    html_to_pdf(
        content_html,
        full_pdf_path,
        title=item.title,
    )
    pdf_item.external_path = full_pdf_path

    return pdf_item
