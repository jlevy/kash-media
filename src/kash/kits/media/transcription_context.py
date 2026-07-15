from __future__ import annotations

from typing import TypedDict

from kash.model import Item, ItemType

TRANSCRIPTION_METADATA_KEY = "transcription"


class TranscriptionMetadata(TypedDict, total=False):
    """
    Recognized fields in the extensible `Item.extra.transcription` payload.
    """

    key_terms: list[str]
    speaker_hints: dict[str, str]


def get_transcription_metadata(item: Item) -> TranscriptionMetadata:
    """
    Read and normalize recognized transcription metadata, ignoring unknown fields.
    """
    raw = (item.extra or {}).get(TRANSCRIPTION_METADATA_KEY)
    if not isinstance(raw, dict):
        return {}

    metadata: TranscriptionMetadata = {}
    raw_terms = raw.get("key_terms")
    if isinstance(raw_terms, list):
        terms = [term.strip() for term in raw_terms if isinstance(term, str) and term.strip()]
        if terms:
            metadata["key_terms"] = list(dict.fromkeys(terms))

    raw_hints = raw.get("speaker_hints")
    if isinstance(raw_hints, dict):
        hints = {
            str(speaker_id): name.strip()
            for speaker_id, name in raw_hints.items()
            if isinstance(name, str) and name.strip()
        }
        if hints:
            metadata["speaker_hints"] = hints

    return metadata


def parse_key_terms(value: str) -> list[str]:
    """
    Parse newline-separated transcription key terms.

    Newlines avoid ambiguity for terms that contain punctuation or commas.
    """
    return list(dict.fromkeys(term.strip() for term in value.splitlines() if term.strip()))


## Tests


def test_get_transcription_metadata_normalizes_known_fields() -> None:
    item = Item(
        type=ItemType.doc,
        extra={
            "transcription": {
                "key_terms": [" SignalFlow ", "SignalFlow", 3],
                "speaker_hints": {0: " Alice Chen ", "1": ""},
                "future_option": True,
            }
        },
    )

    assert get_transcription_metadata(item) == {
        "key_terms": ["SignalFlow"],
        "speaker_hints": {"0": "Alice Chen"},
    }
    assert parse_key_terms("Alice Chen\nSignalFlow\nAlice Chen\n") == [
        "Alice Chen",
        "SignalFlow",
    ]
