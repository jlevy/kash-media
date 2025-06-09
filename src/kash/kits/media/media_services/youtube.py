import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from frontmatter_format import to_yaml_string
from typing_extensions import override

from kash.config.logger import get_logger
from kash.config.text_styles import EMOJI_WARN
from kash.kits.media.utils.yt_dlp_tools import parse_date, ydl_download_media, ydl_extract_info
from kash.model.media_model import (
    SERVICE_YOUTUBE,
    HeatmapValue,
    MediaMetadata,
    MediaService,
    MediaUrlType,
)
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import Url
from kash.utils.common.url_slice import Slice
from kash.utils.errors import ApiResultError, InvalidInput
from kash.utils.file_utils.file_formats_model import MediaType

log = get_logger(__name__)


VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


class YouTube(MediaService):
    @override
    def canonicalize_and_type(self, url: Url) -> tuple[Url | None, MediaUrlType | None]:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")

        if parsed_url.hostname == "youtu.be":
            video_id = self.get_media_id(url)
            if video_id:
                return Url(f"https://www.youtube.com/watch?v={video_id}"), MediaUrlType.video
        elif parsed_url.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
            # Check for channel URLs first, as they have distinct paths
            if (
                len(path_parts) > 0
                and path_parts[0] in ("channel", "c", "user")
                or parsed_url.path.startswith("/@")
            ):
                # It's already a canonical channel URL or a recognized format.
                # TODO: Consider canonicalizing /c/ and /user/ to /@handle if possible?
                return url, MediaUrlType.channel

            query = parse_qs(parsed_url.query)

            # Check for playlist URLs
            if len(path_parts) > 0 and path_parts[0] == "playlist":
                list_id = query.get("list", [""])[0]
                if list_id:
                    return (
                        Url(f"https://www.youtube.com/playlist?list={list_id}"),
                        MediaUrlType.playlist,
                    )

            # Check for /live/ and /shorts/ paths
            if len(path_parts) == 2 and path_parts[0] in ("live", "shorts"):
                video_id = path_parts[1]
                if VIDEO_ID_PATTERN.match(video_id):
                    return Url(f"https://www.youtube.com/watch?v={video_id}"), MediaUrlType.video

            # Fallback to checking ?v= query parameter for standard video URLs
            video_id = query.get("v", [""])[0]
            if video_id and VIDEO_ID_PATTERN.match(video_id):
                return Url(f"https://www.youtube.com/watch?v={video_id}"), MediaUrlType.video

        # If none of the above matched
        return None, None

    @override
    def get_media_id(self, url: Url) -> str | None:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")

        if parsed_url.hostname == "youtu.be":
            video_id = parsed_url.path[1:]
            if VIDEO_ID_PATTERN.match(video_id):
                return video_id
        elif parsed_url.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
            # Check paths first
            if len(path_parts) == 2 and path_parts[0] in ("live", "shorts"):
                video_id = path_parts[1]
                if VIDEO_ID_PATTERN.match(video_id):
                    return video_id

            # Check query parameter
            query = parse_qs(parsed_url.query)
            video_id = query.get("v", [""])[0]
            if video_id and VIDEO_ID_PATTERN.match(video_id):
                return video_id
        return None

    @override
    def thumbnail_url(self, url: Url) -> Url | None:
        id = self.get_media_id(url)
        return Url(f"https://img.youtube.com/vi/{id}/sddefault.jpg") if id else None
        # Others:
        # https://img.youtube.com/vi/{id}/hqdefault.jpg
        # https://img.youtube.com/vi/{id}/maxresdefault.jpg

    @override
    def timestamp_url(self, url: Url, timestamp: float) -> Url:
        canon_url = self.canonicalize(url)
        if not canon_url:
            raise InvalidInput(f"Unrecognized YouTube URL: {url}")
        return Url(canon_url + f"&t={timestamp}s")

    @override
    def download_media(
        self,
        url: Url,
        target_dir: Path,
        *,
        media_types: list[MediaType] | None = None,
        slice: Slice | None = None,
    ) -> dict[MediaType, Path]:
        url = not_none(self.canonicalize(url), "Not a recognized YouTube URL")
        return ydl_download_media(url, target_dir, media_types=media_types, slice=slice)

    def _extract_info(self, url: Url) -> dict[str, Any]:
        url = not_none(self.canonicalize(url), "Not a recognized YouTube URL")
        return ydl_extract_info(url)

    @override
    def metadata(self, url: Url, full: bool = False) -> MediaMetadata:
        url = not_none(self.canonicalize(url), "Not a recognized YouTube URL")
        yt_result: dict[str, Any] = self._extract_info(url)

        return self._parse_metadata(yt_result, full=full)

    @override
    def list_channel_items(self, url: Url) -> list[MediaMetadata]:
        """
        Get all video URLs and metadata from a YouTube channel or playlist.
        """

        result = self._extract_info(url)

        if "entries" in result:
            entries = result["entries"]
        else:
            log.warning("%s No videos found in the channel.", EMOJI_WARN)
            entries = []

        video_meta_list: list[MediaMetadata] = []

        # TODO: Inspect and collect rest of the metadata here, like upload date etc.
        for value in entries:
            if "entries" in value:
                # For channels there is a list of values each with their own videos.
                video_meta_list.extend(self._parse_metadata(e) for e in value["entries"])
            else:
                # For playlists, entries holds the videos.
                video_meta_list.append(self._parse_metadata(value))

        log.message("Found %d videos in channel %s", len(video_meta_list), url)

        return video_meta_list

    def _parse_metadata(
        self, yt_result: dict[str, Any], full: bool = False, **overrides: dict[str, Any]
    ) -> MediaMetadata:
        try:
            media_id = yt_result["id"]  # Renamed for clarity.
            if not media_id:
                raise KeyError("No ID found")

            url = yt_result.get("webpage_url") or yt_result.get("url")
            if not url:
                raise KeyError("No URL found")

            thumbnail_url = self.thumbnail_url(Url(url))
            # thumbnail_url = best_thumbnail(yt_result)  # Alternate approach, but messier.

            # FIXME: upload_date not working?
            # Apparently upload_date is in full video metadata but not channel metadata.
            upload_date_str = yt_result.get("upload_date")
            upload_date = parse_date(upload_date_str) if upload_date_str else None

            # Heatmap is interesting but verbose so skipping by default.
            heatmap = None
            if full:
                heatmap = [HeatmapValue(**h) for h in yt_result.get("heatmap", [])] or None

            result = MediaMetadata(
                media_id=media_id,
                media_service=SERVICE_YOUTUBE,
                url=url,
                thumbnail_url=thumbnail_url,
                title=yt_result["title"],
                description=yt_result["description"],
                upload_date=upload_date,
                channel_url=Url(yt_result["channel_url"]),
                view_count=yt_result.get("view_count"),
                duration=yt_result.get("duration"),
                heatmap=heatmap,
                **overrides,
            )
            log.message("Parsed YouTube metadata: %s", result)
        except KeyError as e:
            log.error("Missing key in YouTube metadata (see saved object): %s", e)
            log.save_object(
                "yt_dlp result", None, to_yaml_string(yt_result, stringify_unknown=True)
            )
            raise ApiResultError("Did not find key in YouTube metadata: %s" % e)

        return result


def best_thumbnail(data: dict[str, Any]) -> Url | None:
    """
    Get the best thumbnail from YouTube metadata, which is of the form:
    {
        'thumbnails': [
            {'url': 'https://i.ytimg.com/vi/gc417NquXbk/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLC7F70CUSkwqkrgEwKX1AmXCJ8jsQ', 'height': 94, 'width': 168},
            {'url': 'https://i.ytimg.com/vi/gc417NquXbk/hqdefault.jpg?sqp=-oaymwEbCMQBEG5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLA6pIOQRUlixQogTAR0NAv3zJgxqQ', 'height': 110, 'width': 196},
            {'url': 'https://i.ytimg.com/vi/gc417NquXbk/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLC7zW8Hu59MgQkRPX4WsVpc-tkxxQ', 'height': 138, 'width': 246},
            {'url': 'https://i.ytimg.com/vi/gc417NquXbk/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLB7nBpvNKwCwrtr_lv85T0GITOFjA', 'height': 188, 'width': 336},
        ],
    }
    """
    thumbnail_url = None
    try:
        thumbnails = data["thumbnails"]
        if not isinstance(thumbnails, list):
            return None
        largest_thumbnail = max(thumbnails, key=lambda x: x.get("width", 0))
        thumbnail_url = largest_thumbnail.get("url", None)
    except (KeyError, TypeError):
        pass

    if not thumbnail_url:
        thumbnail_url = data.get("thumbnail")

    return Url(thumbnail_url) if thumbnail_url else None


## Tests


def test_canonicalize_youtube():
    youtube = YouTube()

    def assert_canon(url: str, expected_canon_url: str | None, expected_type: MediaUrlType | None):
        canon_url, url_type = youtube.canonicalize_and_type(Url(url))
        assert canon_url == (Url(expected_canon_url) if expected_canon_url else None)
        assert url_type == expected_type
        # Also test canonicalize convenience method
        if expected_canon_url:
            assert youtube.canonicalize(Url(url)) == Url(expected_canon_url)
        else:
            assert youtube.canonicalize(Url(url)) is None

    # Video URLs
    assert_canon(
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        MediaUrlType.video,
    )
    assert_canon(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        MediaUrlType.video,
    )
    assert_canon(
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ&feature=share",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        MediaUrlType.video,
    )
    assert_canon(
        "https://www.youtube.com/watch?v=_5y0AalUDh4&list=PL9XbNw3iJu1zKJRyV3Jz3rqlFV1XJfvNv&index=12",
        "https://www.youtube.com/watch?v=_5y0AalUDh4",
        MediaUrlType.video,
    )

    # Live URLs
    assert_canon(
        "https://www.youtube.com/live/XVwpL_cAvrw?si=mgv-xnhaO6UJLxwb",
        "https://www.youtube.com/watch?v=XVwpL_cAvrw",
        MediaUrlType.video,
    )

    # Shorts URLs
    assert_canon(
        "https://www.youtube.com/shorts/abcdefghijk",  # Example valid ID format
        "https://www.youtube.com/watch?v=abcdefghijk",
        MediaUrlType.video,
    )
    assert_canon(
        "https://youtube.com/shorts/lmnopqrs_tu",  # Example valid ID format (11 chars)
        "https://www.youtube.com/watch?v=lmnopqrs_tu",
        MediaUrlType.video,
    )

    # Channel URLs
    assert_canon(
        "https://www.youtube.com/@hubermanlab",
        "https://www.youtube.com/@hubermanlab",
        MediaUrlType.channel,
    )
    assert_canon(
        "https://www.youtube.com/c/inanutshell",
        "https://www.youtube.com/c/inanutshell",
        MediaUrlType.channel,
    )
    assert_canon(
        "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw",
        "https://www.youtube.com/channel/UCXuqSBlHAE6Xw-yeJA0Tunw",
        MediaUrlType.channel,
    )
    assert_canon(
        "https://www.youtube.com/user/Vsauce",
        "https://www.youtube.com/user/Vsauce",
        MediaUrlType.channel,
    )

    # Playlist URLs
    assert_canon(
        "https://youtube.com/playlist?list=PLPNW_gerXa4N_PVVoq0Za03YKASSGCazr&si=9IVO8p-ZwmMLI18F",
        "https://www.youtube.com/playlist?list=PLPNW_gerXa4N_PVVoq0Za03YKASSGCazr",
        MediaUrlType.playlist,
    )
    assert_canon(
        "https://www.youtube.com/playlist?list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo",
        "https://www.youtube.com/playlist?list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo",
        MediaUrlType.playlist,
    )

    # Invalid/Unrecognized URLs
    assert_canon("https://example.com", None, None)
    assert_canon("https://www.youtube.com/", None, None)
    assert_canon(
        "https://www.youtube.com/feed/subscriptions", None, None
    )  # Example non-content URL
    assert_canon("https://youtu.be/", None, None)  # Missing ID
    assert_canon("https://www.youtube.com/watch?list=abc", None, None)  # Missing v= parameter
