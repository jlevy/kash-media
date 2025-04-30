import logging
import re

import rich
from ruamel.yaml.comments import LineCol

log = logging.getLogger(__name__)


def check_endnotes(text: str) -> tuple[list[int], list[int]]:
    """
    Finds potential endnote markers.
    Returns a tuple containing two lists:
        1. Sorted unique numbers from <sup>n</sup> tags.
        2. Sorted unique numbers from 'n. ' list items.
    """
    # 1) find all <sup>n</sup> markers
    sups = re.findall(r"<sup>(\d+)</sup>", text)
    sup_nums = sorted({int(n) for n in sups})

    # 2) find all list-item numbers in the document
    ends = re.findall(r"^\s*(\d+)\.\s+", text, flags=re.MULTILINE)
    end_nums = sorted({int(n) for n in ends})

    # Check for contiguity only if both lists seem to match initially
    if sup_nums and sup_nums == end_nums:
        # Check if the sequence is contiguous starting from 1 or the first found number
        first = sup_nums[0]
        if sup_nums != list(range(first, sup_nums[-1] + 1)):
            # Treat as mismatch if not contiguous
            return sup_nums, []  # Return non-matching lists

    return sup_nums, end_nums


_FOOTNOTE_INDENT = "    "


def convert_endnotes_to_footnotes(text: str, strict: bool = True) -> str:
    """
    Detects and converts docx-style endnotes (superscript footnotes marked with
    `<sup>n</sup>` tags and an enumerated list of notes) to GitHub-style footnotes.

    Returns original text if there are no endnotes (no <sup> tags are found).
    Raises `ValueError` if superscripts are present but list numbers don't match
    or are non-contiguous.
    """

    sup_nums, end_nums = check_endnotes(text)

    # If no superscripts, assume no endnotes to convert
    if not sup_nums:
        return text

    # If superscripts exist but don't match endnote numbers (or were non-contiguous)
    if sup_nums != end_nums and strict:
        raise ValueError(
            f"Superscript numbers {sup_nums!r} do not match endnote list numbers {end_nums!r}"
        )
    else:
        log.warning(
            f"Superscript numbers {sup_nums!r} do not match endnote list numbers {end_nums!r}"
        )

    # Use the validated superscript numbers
    unique_sup_nums = sup_nums

    # 1) Split into lines, locate the first enumerated endnote
    lines = text.splitlines()
    start_line = next((i for i, line in enumerate(lines) if re.match(r"\s*\d+\.\s+", line)), None)
    # This check should technically be redundant now due to check_endnotes,
    # but kept for safety.
    if start_line is None:
        raise ValueError(
            "Detected <sup> tags but no enumerated endnote block found."
        )  # pragma: no cover

    # 2) If the line immediately before is a header, preserve it; else no header
    header_line = start_line - 1
    preserve_header = None
    if header_line >= 0 and lines[header_line].lstrip().startswith("#"):
        preserve_header = lines[header_line]

    # 3) Parse the endnote block into a dict { number -> text }
    endnotes: dict[int, list[str]] = {}
    current = None
    for line in lines[start_line:]:
        m = re.match(r"\s*(\d+)\.\s+(.*)", line)
        line_stripped = line.strip()
        if m:
            num = int(m.group(1))
            # Only parse notes corresponding to the detected unique numbers

            current = num
            if num in endnotes:
                log.warning("Duplicate footnote %s: %r", num, line)
            if num not in unique_sup_nums:
                log.warning("Endnote %s didn't have a corresponding <sup> tag: %r", num, line)
            endnotes[num] = [m.group(2).rstrip()]
        elif current is not None and (not line_stripped or line.startswith(" ")):
            # Continuation lines are empty or indented.
            if current in endnotes and line_stripped:
                endnotes[current].append(line_stripped)
        elif not line.startswith(" "):
            # A non-indented line so end current footnote.
            current = None

    # 4) Build the footnote definitions
    footnote_defs: list[str] = []
    for num in endnotes:
        # Handle cases where a note number might be missing due to parsing issues
        # though the initial check should prevent this.
        body = f"\n{_FOOTNOTE_INDENT}".join(endnotes.get(num, [""])).strip()
        footnote_defs.append(f"[^{num}]: {body}")

    # 5) Replace all <sup>n</sup> -> [^n]
    def _rep(m: re.Match[str]) -> str:
        return f"[^{m.group(1)}]"

    body_text = re.sub(r"<sup>(\d+)</sup>", _rep, text)

    # Split the modified text to get lines with replacements
    modified_lines = body_text.splitlines()

    # 6) Re-slice out the original endnote block (and optional header)
    #    Indices (cut_start) are based on the *original* lines structure
    cut_start = header_line if preserve_header else start_line
    # Use the modified_lines to build the new body
    new_body = "\n".join(modified_lines[:cut_start]).rstrip()

    # 7) Assemble final document:
    parts = [new_body]
    if preserve_header:
        parts.append(preserve_header)
    parts.extend(footnote_defs)

    return "\n\n".join(parts) + "\n"


## Tests


def test_endnotes_conversion():
    from textwrap import dedent

    # 1) simple endnotes detection & conversion
    md = dedent("""
    Hello, world<sup>1</sup> and again<sup>2</sup>.
    More text.
    1. First note
    2. Second note
    """)

    converted = convert_endnotes_to_footnotes(md)
    # superscripts replaced
    assert "world[^1]" in converted
    assert "again[^2]" in converted
    # definitions appended
    assert "[^1]: First note" in converted
    assert "[^2]: Second note" in converted
    # Original superscripts should be gone
    assert "<sup>1</sup>" not in converted
    assert "<sup>2</sup>" not in converted

    # No endnotes
    plain = "Just some text without endnotes."
    # Check it returns unchanged
    assert convert_endnotes_to_footnotes(plain) == plain

    # Mismatch between <sup>…</sup> and list numbers → error
    bad_mismatch = "Oops<sup>1</sup><sup>3</sup>\n\n1. Only one definition\n3. Third def"
    try:
        convert_endnotes_to_footnotes(bad_mismatch)
    except ValueError as e:
        assert "do not match" in str(e)
    else:
        raise AssertionError("Expected ValueError for mismatch")

    # Non-contiguous superscripts -> error
    bad_non_contig_sup = "Oops<sup>1</sup><sup>3</sup>\n\n1. Def one\n3. Def three"
    try:
        convert_endnotes_to_footnotes(bad_non_contig_sup)
    except ValueError as e:
        assert "Superscript numbers [1, 3]" in str(e)
        assert "do not match endnote list numbers []" in str(
            e
        )  # Because check_endnotes returns empty list for end_nums on contiguity failure
    else:
        raise AssertionError("Expected ValueError for non-contiguous superscripts")

    # Non-contiguous list numbers -> error
    bad_non_contig_list = "Oops<sup>1</sup><sup>2</sup>\n\n1. Def one\n3. Def three"
    try:
        convert_endnotes_to_footnotes(bad_non_contig_list)
    except ValueError as e:
        assert "Superscript numbers [1, 2]" in str(e)
        assert "do not match endnote list numbers [1, 3]" in str(e)
    else:
        raise AssertionError("Expected ValueError for non-contiguous list")

    # Test with header preservation
    md_with_header = dedent("""
    Some text<sup>1</sup>.

    ## Notes

    1. The note.
    """)
    converted_header = convert_endnotes_to_footnotes(md_with_header)
    assert "Some text[^1]." in converted_header
    assert "\n\n## Notes\n\n" in converted_header  # Header preserved
    assert "[^1]: The note." in converted_header
    assert "1. The note." not in converted_header  # Original list removed

    # Test multiline notes
    md_multiline = dedent("""
    Point<sup>1</sup>.

    1. This is the first line.
       This is the second line.

       This is the third line.

    This is not in the footnote.
    """)
    converted_multiline = convert_endnotes_to_footnotes(md_multiline)
    print(converted_multiline)
    assert "[^1]: This is the first line." in converted_multiline
    assert "    This is the second line." in converted_multiline
    assert "    This is the third line." in converted_multiline
    assert "This is not in the footnote." not in converted_multiline
