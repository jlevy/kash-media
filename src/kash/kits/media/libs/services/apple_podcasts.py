from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from frontmatter_format import to_yaml_string
from typing_extensions import override
from yt_dlp.utils import DownloadError

from kash.config.logger import get_logger
from kash.config.text_styles import EMOJI_WARN
from kash.kits.media.libs.yt_dlp_tools import ydl_download_media, ydl_extract_info
from kash.model.media_model import SERVICE_APPLE_PODCASTS, MediaMetadata, MediaService, MediaUrlType
from kash.utils.common.type_utils import not_none
from kash.utils.common.url import Url
from kash.utils.errors import ApiResultError
from kash.utils.file_utils.file_formats_model import MediaType

log = get_logger(__name__)


# URL format is podcast id and episode id:
# https://podcasts.apple.com/us/podcast/upper-priest-lake-trail-to-continental-creek-trail/id1303792223?i=1000394194840
# which is equivalent to
# https://podcasts.apple.com/podcast/id1303792223?i=1000394194840
# See:
# https://podcasters.apple.com/support/847-hosts-and-guests

# mypy is falsely complaining.
# mypy: disable-error-code="override,misc"


class ApplePodcasts(MediaService):
    @override
    def canonicalize_and_type(self, url: Url) -> tuple[Url | None, MediaUrlType | None]:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ("podcasts.apple.com", "itunes.apple.com"):
            path_parts = parsed_url.path.split("/")
            for part in path_parts:
                if part.startswith("id"):
                    podcast_id = part
                    query = parse_qs(parsed_url.query)
                    episode_id = query.get("i", [None])[0]
                    if episode_id:
                        return (
                            Url(f"https://podcasts.apple.com/podcast/{podcast_id}?i={episode_id}"),
                            MediaUrlType.episode,
                        )
                    return (
                        Url(f"https://podcasts.apple.com/podcast/{podcast_id}"),
                        MediaUrlType.podcast,
                    )
        return None, None

    @override
    def get_media_id(self, url: Url) -> str | None:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ("podcasts.apple.com", "itunes.apple.com"):
            path_parts = parsed_url.path.split("/")
            for part in path_parts:
                if part.startswith("id"):
                    podcast_id = part
                    query = parse_qs(parsed_url.query)
                    episode_id = query.get("i", [None])[0]
                    if episode_id:
                        return f"{podcast_id}?i={episode_id}"
        return None

    @override
    def metadata(self, url: Url, full: bool = False) -> MediaMetadata:
        url = not_none(self.canonicalize(url), "Not a recognized Apple Podcasts URL")
        yt_result: dict[str, Any] = self._extract_info(url)

        return self._parse_metadata(yt_result, full=full)

    @override
    def thumbnail_url(self, url: Url) -> Url | None:
        # Apple Podcasts doesn't have a standardized thumbnail URL format.
        # We'll need to extract this from the metadata.
        try:
            metadata = self.metadata(url)
            return metadata.thumbnail_url if metadata else None
        except DownloadError as e:
            log.warning("Could not get a thumbnail URL; will omit thumbnail: %s", e)
            return None

    @override
    def timestamp_url(self, url: Url, timestamp: float) -> Url:
        # Apple Podcasts doesn't support timestamp links. We'll return the original URL.
        return url

    @override
    def download_media(
        self, url: Url, target_dir: Path, media_types: list[MediaType] | None = None
    ) -> dict[MediaType, Path]:
        url = not_none(self.canonicalize(url), "Not a recognized Apple Podcasts URL")
        return ydl_download_media(url, target_dir, media_types)

    def _extract_info(self, url: Url) -> dict[str, Any]:
        url = not_none(self.canonicalize(url), "Not a recognized Apple Podcasts URL")
        return ydl_extract_info(url)

    @override
    def list_channel_items(self, url: Url) -> list[MediaMetadata]:
        result = self._extract_info(url)

        if "entries" in result:
            entries = result["entries"]
        else:
            log.warning("%s No episodes found in the podcast.", EMOJI_WARN)
            entries = []

        episode_meta_list: list[MediaMetadata] = []

        for entry in entries:
            episode_meta_list.append(self._parse_metadata(entry))

        log.message("Found %d episodes in podcast %s", len(episode_meta_list), url)

        return episode_meta_list

    def _parse_metadata(
        self,
        yt_result: dict[str, Any],
        full: bool = False,
        **overrides: dict[str, Any],
    ) -> MediaMetadata:
        try:
            media_id = yt_result["id"]
            if not media_id:
                raise KeyError("No ID found")

            url = yt_result.get("webpage_url") or yt_result.get("url")
            if not url:
                raise KeyError("No URL found")

            thumbnail_url = yt_result.get("thumbnail")

            upload_date_str = yt_result.get("upload_date")
            upload_date = date.fromisoformat(upload_date_str) if upload_date_str else None

            result = MediaMetadata(
                media_id=media_id,
                media_service=SERVICE_APPLE_PODCASTS,
                url=url,
                thumbnail_url=thumbnail_url,
                title=yt_result["title"],
                description=yt_result.get("description"),
                upload_date=upload_date,
                channel_url=Url(yt_result.get("channel_url", "")),
                view_count=yt_result.get("view_count"),
                duration=yt_result.get("duration"),
                heatmap=None,
                **overrides,
            )
            log.message("Parsed Apple Podcasts metadata: %s", result)
        except KeyError as e:
            log.error("Missing key in Apple Podcasts metadata (see saved object): %s", e)
            log.save_object(
                "yt_dlp result", None, to_yaml_string(yt_result, stringify_unknown=True)
            )
            raise ApiResultError("Did not find key in Apple Podcasts metadata: %s" % e)

        return result


## Tests


def test_canonicalize_apple():
    apple = ApplePodcasts()

    assert apple.get_media_id(Url("https://podcasts.apple.com/us/podcast/id1627920305")) is None
    assert apple.get_media_id(Url("https://podcasts.apple.com/podcast/id1234567890")) is None
    assert apple.get_media_id(Url("https://example.com/podcast/123")) is None

    assert (
        apple.get_media_id(Url("https://podcasts.apple.com/podcast/id1234567890?i=1000635337486"))
        == "id1234567890?i=1000635337486"
    )

    def assert_canon(url: str, canon_url: str):
        assert apple.canonicalize(Url(url)) == Url(canon_url)

    assert_canon(
        "https://podcasts.apple.com/us/podcast/redefining-success-money-and-belonging-paul-millerd/id1627920305?i=1000635337486",
        "https://podcasts.apple.com/podcast/id1627920305?i=1000635337486",
    )

    assert_canon(
        "https://podcasts.apple.com/us/podcast/redefining-success-money-and-belonging-paul-millerd/id1627920305?i=1000635337486",
        "https://podcasts.apple.com/podcast/id1627920305?i=1000635337486",
    )
