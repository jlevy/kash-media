import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import yt_dlp
from clideps.pkgs.pkg_check import pkg_check
from clideps.pkgs.pkg_types import Platform
from frontmatter_format import to_yaml_string

from kash.config.logger import get_logger
from kash.utils.common.url import Url
from kash.utils.common.url_slice import Slice
from kash.utils.errors import ApiResultError
from kash.utils.file_utils.file_formats_model import MediaType

log = get_logger(__name__)


def parse_date(upload_date: str | date) -> date:
    if isinstance(upload_date, str):
        return date.fromisoformat(upload_date)
    elif isinstance(upload_date, date):
        return upload_date
    raise ValueError(f"Invalid date: {upload_date}")


def ydl_extract_info(url: Url) -> dict[str, Any]:
    ydl_opts = {
        "extract_flat": "in_playlist",  # Extract metadata only, without downloading.
        "quiet": True,
        "dump_single_json": True,
        "logger": log,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(str(url), download=False)

        log.save_object("yt_dlp result", None, to_yaml_string(result, stringify_unknown=True))

        if not isinstance(result, dict):
            raise ApiResultError(f"Unexpected result from yt_dlp: {result}")

        return result


def ydl_download_media(
    url: Url,
    target_dir: Path | None = None,
    media_types: list[MediaType] | None = None,
    slice: Slice | None = None,
) -> dict[MediaType, Path]:
    """
    Download and convert to mp3 and mp4 using yt_dlp, which is generally the best
    library for this.
    """
    # We need ffmpeg CLI. On Linux we also need libgl1 (has several names but clideps
    # knows about it).
    pkg_check().require("ffmpeg")
    pkg_check().require("libgl1", on_platforms=[Platform.Linux])

    if not media_types:
        media_types = [MediaType.audio, MediaType.video]

    temp_dir = target_dir or tempfile.mkdtemp()
    ydl_opts: dict[str, Any]
    if MediaType.video in media_types:
        ydl_opts = {
            # Try for best video+audio, fall back to best available.
            # Might want to support smaller sizes tho.
            # "format": "bestvideo[height<=720]+bestaudio/best",
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "media.%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",  # Yep, it's really spelled this way in yt_dlp.
                },
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
            ],
            "keepvideo": True,  # By default yt_dlp will delete the video file.
        }
    else:
        ydl_opts = {
            # Try for best video+audio, fall back to best available.
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "media.%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
            ],
        }

    # Add time slicing support if slice is provided
    if slice:
        # Tell yt-dlp the exact seconds we want
        ydl_opts["download_ranges"] = yt_dlp.download_range_func(
            None, [(slice.start_time, slice.end_time)]
        )
        ydl_opts["force_keyframes_at_cuts"] = True

        # Let yt-dlp choose the best format automatically
        # Just exclude problematic HLS formats
        ydl_opts["format"] = "best[protocol!=m3u8][protocol!=m3u8_native]/best"

        log.info("Slice requested: %s", (slice.start_time, slice.end_time))

        # This could be more robust but was triggering ffmpeg errors.
        # ydl_opts["format"] = (
        #     # 1. DASH video in fragments + any best audio
        #     "bestvideo[protocol*=http_dash_segments]+bestaudio/"
        #     # 2. otherwise: segmented HLS (yt-dlp will use its native downloader)
        #     "(bv*+ba/best)[protocol*=m3u8]/"
        #     # 3. last resort: whatever is “best” (could be progressive MP4)
        #     "best"
        # )
        # ydl_opts["hls_prefer_native"] = True

    # Use our logger.
    ydl_opts["logger"] = log  # pylance: ignore

    log.info("Extracting media from %s at %s using ydl_opts: %s", url, temp_dir, ydl_opts)

    info_dict = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        media_file_path = ydl.prepare_filename(info_dict)

    result_paths = {}

    log.info("ydl output filename: %s", media_file_path)

    # Check audio and video files exist.
    if MediaType.audio in media_types:
        mp3_path = os.path.splitext(media_file_path)[0] + ".mp3"
        if os.path.exists(mp3_path):
            result_paths[MediaType.audio] = Path(mp3_path)
        else:
            log.warning("mp3 download not found: %s", mp3_path)
    if MediaType.video in media_types:
        mp4_path = os.path.splitext(media_file_path)[0] + ".mp4"
        if os.path.exists(mp4_path):
            result_paths[MediaType.video] = Path(mp4_path)
        else:
            log.warning("mp4 download not found: %s", mp4_path)

    return result_paths
