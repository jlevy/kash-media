import sys
from typing import Any, BinaryIO

import mammoth
from markitdown._base_converter import DocumentConverterResult
from markitdown._exceptions import MISSING_DEPENDENCY_MESSAGE, MissingDependencyException
from markitdown._stream_info import StreamInfo
from markitdown.converters._docx_converter import DocxConverter
from typing_extensions import override

# Based on markitdown.converters._docx_converter.DocxConverter.

_dependency_exc_info = None
try:
    import mammoth
except ImportError:
    _dependency_exc_info = sys.exc_info()

# Accepted types (copied exactly from original DocxConverter)
ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]
ACCEPTED_FILE_EXTENSIONS = [".docx"]


class CustomDocxConverter(DocxConverter):
    """
    A custom DocxConverter derived from the original, modified to allow passing Markdownify
    options to the underlying Markdownify HtmlConverter.

    See options:
    https://github.com/matthewwithanm/python-markdownify
    """

    def __init__(self, markdownify_options: dict[str, Any] | None = None):
        """
        Initializes the converter, storing custom markdownify options.
        """
        super().__init__()  # Call base class init (initializes self._html_converter)
        # Store custom options for markdownify
        self.markdownify_options = markdownify_options if markdownify_options is not None else {}  # pyright: ignore

    @override
    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options passed from MarkItDown.convert (e.g., llm_client)
    ) -> DocumentConverterResult:
        """
        Converts the DOCX stream using mammoth, then converts the resulting
        HTML to Markdown using the internal HtmlConverter, passing along
        any stored markdownify options.
        """
        # Same as original DocxConverter:
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".docx",
                    feature="docx",
                )
            ) from _dependency_exc_info[1].with_traceback(  # type: ignore[union-attr]  # pyright: ignore
                _dependency_exc_info[2]
            )

        # Customized form MarkItDown:

        # Extract mammoth-specific options if any are passed via kwargs.
        style_map = kwargs.get("style_map", None)

        html_result = mammoth.convert_to_html(file_stream, style_map=style_map)
        html_content = html_result.value

        # Add custom markdownify options to the kwargs.
        combined_options = {**kwargs, **self.markdownify_options}

        return self._html_converter.convert_string(
            html_content, url=stream_info.url, **combined_options
        )
