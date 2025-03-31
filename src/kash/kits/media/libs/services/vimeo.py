import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from typing_extensions import override

from kash.config.logger import get_logger
from kash.kits.media.libs.yt_dlp_tools import parse_date, ydl_download_media, ydl_extract_info
from kash.model.media_model import MediaMetadata, MediaService, MediaUrlType
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import Url
from kash.utils.errors import ApiResultError, InvalidInput
from kash.utils.file_utils.file_formats_model import MediaType

log = get_logger(__name__)


VIDEO_PATTERN = r"^/(\d+)$"
CHANNEL_PATTERN = r"^/([a-zA-Z0-9_-]+)$"


# mypy is falsely complaining.
# mypy: disable-error-code="override,misc"


class Vimeo(MediaService):
    @override
    def canonicalize_and_type(self, url: Url) -> tuple[Url | None, MediaUrlType | None]:
        parsed_url = urlparse(url)
        if parsed_url.hostname == "vimeo.com":
            path = parsed_url.path
            video_match = re.match(VIDEO_PATTERN, path)
            if video_match:
                return Url(f"https://vimeo.com/{video_match.group(1)}"), MediaUrlType.video
            channel_match = re.match(CHANNEL_PATTERN, path)
            if channel_match:
                return Url(f"https://vimeo.com/{channel_match.group(1)}"), MediaUrlType.channel
        return None, None

    @override
    def get_media_id(self, url: Url) -> str | None:
        parsed_url = urlparse(url)
        if parsed_url.hostname == "vimeo.com":
            path = parsed_url.path
            video_match = re.match(VIDEO_PATTERN, path)
            if video_match:
                return f"video:{video_match.group(1)}"
            channel_match = re.match(CHANNEL_PATTERN, path)
            if channel_match:
                return f"channel:{channel_match.group(1)}"
        return None

    @override
    def metadata(self, url: Url, full: bool = False) -> MediaMetadata:
        url = not_none(self.canonicalize(url), "Not a recognized Vimeo URL")
        vimeo_result: dict[str, Any] = self._extract_info(url)
        return self._parse_metadata(vimeo_result, full=full)

    @override
    def thumbnail_url(self, url: Url) -> Url | None:
        vimeo_result = self._extract_info(url)
        thumbnails = vimeo_result.get("thumbnails", [])
        if thumbnails:
            return Url(thumbnails[-1]["url"])  # Get the last (usually highest quality) thumbnail
        return None

    @override
    def timestamp_url(self, url: Url, timestamp: float) -> Url:
        canon_url, url_type = self.canonicalize_and_type(url)
        if not canon_url:
            raise InvalidInput(f"Unrecognized Vimeo URL: {url}")
        if url_type == MediaUrlType.video:
            return Url(f"{canon_url}#t={timestamp}")
        return canon_url  # For channels, just return the canonical URL

    @override
    def download_media(
        self, url: Url, target_dir: Path, media_types: list[MediaType] | None = None
    ) -> dict[MediaType, Path]:
        url = not_none(self.canonicalize(url), "Not a recognized Vimeo URL")
        return ydl_download_media(url, target_dir, media_types)

    @override
    def list_channel_items(self, url: Url) -> list[MediaMetadata]:
        raise NotImplementedError()

    def _extract_info(self, url: Url) -> dict[str, Any]:
        url = not_none(self.canonicalize(url), "Not a recognized Vimeo URL")
        return ydl_extract_info(url)

    def _parse_metadata(
        self, vimeo_result: dict[str, Any], full: bool = False, **overrides: dict[str, Any]
    ) -> MediaMetadata:
        try:
            media_id = vimeo_result["id"]
            if not media_id:
                raise KeyError("No ID found")

            url = vimeo_result.get("webpage_url") or vimeo_result.get("url")
            if not url:
                raise KeyError("No URL found")

            thumbnail_url = self.thumbnail_url(Url(url))

            upload_date_str = vimeo_result.get("upload_date")
            upload_date = parse_date(upload_date_str) if upload_date_str else None

            _, url_type = self.canonicalize_and_type(Url(url))

            result = MediaMetadata(
                media_id=media_id,
                media_service="vimeo",
                url=url,
                thumbnail_url=thumbnail_url,
                title=vimeo_result["title"],
                description=vimeo_result.get("description"),
                upload_date=upload_date,
                channel_url=Url(vimeo_result.get("uploader_url", "")),
                view_count=vimeo_result.get("view_count"),
                duration=vimeo_result.get("duration") if url_type == MediaUrlType.video else None,
                heatmap=None,
                **overrides,
            )
            log.message("Parsed Vimeo metadata: %s", result)
        except KeyError as e:
            log.error("Missing key in Vimeo metadata: %s", e)
            raise ApiResultError(f"Did not find key in Vimeo metadata: {e}")

        return result
