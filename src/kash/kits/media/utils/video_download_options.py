from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MAX_HEIGHT = 1080
"""
Cap on video height when a caller expresses no preference.

Video is fetched to be watched in a popover and to have still frames pulled from it,
neither of which benefits from 4K. Uncapped `bestvideo` on a long source costs gigabytes
of download and, worse, usually lands on a codec that then has to be re-encoded.
"""


@dataclass(frozen=True)
class VideoDownloadOptions:
    """
    How much video to fetch and how to package it.

    Exists so callers can trade quality against time and disk without a library change:
    a frame-capture job wants something small and fast, an archival copy may want
    everything.
    """

    max_height: int | None = DEFAULT_MAX_HEIGHT
    """Maximum video height in pixels. None fetches the best available."""

    prefer_compatible: bool = True
    """
    Prefer streams that already fit an mp4 container (h264/aac) over higher-quality
    ones that do not.

    This is what avoids re-encoding. YouTube's best streams are usually VP9 or AV1 in
    webm; packaging those as mp4 means a full transcode, which on a multi-hour source
    costs hours of CPU. Preferring compatible streams lets the container change be a
    stream copy instead.
    """

    format_selector: str | None = None
    """Full yt-dlp format selector, overriding everything above."""

    def to_format_selector(self) -> str:
        """The yt-dlp format string for these options."""
        if self.format_selector:
            return self.format_selector

        height = f"[height<={self.max_height}]" if self.max_height else ""
        if not self.prefer_compatible:
            return f"bestvideo{height}+bestaudio/best{height}/best"

        # Ordered by how little work and how few bytes each choice costs. H.264 with
        # AAC remuxes without re-encoding and is the smallest sane option at a given
        # resolution: asking only for "best mp4" selects the highest bitrate, which on
        # YouTube is a Premium VP9 stream several times larger than ordinary H.264 at
        # the same height, often with no size metadata to warn you.
        return (
            f"bestvideo{height}[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo{height}[ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo{height}+bestaudio/"
            f"best{height}/best"
        )


DEFAULT_VIDEO_OPTIONS = VideoDownloadOptions()
"""Used when a caller passes nothing, so existing call sites keep working."""


## Tests


def test_default_selector_prefers_compatible_and_caps_height() -> None:
    selector = VideoDownloadOptions().to_format_selector()

    assert selector.startswith(
        f"bestvideo[height<={DEFAULT_MAX_HEIGHT}][vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]"
    )
    # Falls back to any mp4 pair before giving up on the container.
    assert "[ext=mp4]+bestaudio[ext=m4a]/" in selector
    # Always keeps a fallback so an unusual source still downloads.
    assert selector.endswith("/best")


def test_callers_can_lift_the_cap_or_the_preference() -> None:
    uncapped = VideoDownloadOptions(max_height=None).to_format_selector()
    assert "height<=" not in uncapped

    raw = VideoDownloadOptions(prefer_compatible=False).to_format_selector()
    assert "ext=mp4" not in raw
    assert "avc1" not in raw
    assert "avc1" not in raw

    small = VideoDownloadOptions(max_height=480).to_format_selector()
    assert "[height<=480]" in small


def test_explicit_selector_overrides_everything() -> None:
    options = VideoDownloadOptions(max_height=480, format_selector="worstvideo+worstaudio")

    assert options.to_format_selector() == "worstvideo+worstaudio"
