from dataclasses import asdict, dataclass

from frontmatter_format import to_yaml_string

from kash.config.logger import get_logger
from kash.kits.media.libs import media_templates_dir
from kash.kits.media.libs.media_preconditions import is_youtube_video
from kash.llm_utils.clean_headings import clean_heading, summary_heading
from kash.media_base.media_services import get_media_id
from kash.model.items_model import Item, ItemType
from kash.utils.common.type_utils import as_dataclass
from kash.utils.errors import InvalidInput
from kash.utils.file_utils.file_formats_model import Format
from kash.web_gen import base_templates_dir
from kash.web_gen.template_render import render_web_template
from kash.workspaces.source_items import find_upstream_item

log = get_logger(__name__)


@dataclass
class VideoInfo:
    youtube_id: str
    title: str
    description: str
    topics: list[str]


@dataclass
class VideoGallery:
    title: str
    videos: list[VideoInfo]


def video_gallery_config(items: list[Item]) -> Item:
    """
    Get an item with the config for a video gallery.
    """
    videos = []
    for item in items:
        source_item = find_upstream_item(item, is_youtube_video)

        youtube_id = get_media_id(source_item.url)
        log.message(
            "Pulling video from source item: %s: %s", source_item.store_path, source_item.url
        )
        if not youtube_id or not is_youtube_video(source_item):
            raise InvalidInput(f"Item must be a YouTube URL with id: {source_item}")

        video_info = VideoInfo(
            youtube_id=youtube_id,
            title=clean_heading(item.abbrev_title()),
            description=item.abbrev_description(),
            topics=[],  # TODO
        )
        videos.append(video_info)

    title = summary_heading([video.title for video in videos])
    gallery = VideoGallery(title=title, videos=videos)

    config_item = Item(
        title=f"Config for {title}",
        type=ItemType.config,
        format=Format.yaml,
        body=to_yaml_string(asdict(gallery)),
    )
    return config_item


def video_gallery_generate(config_item: Item) -> str:
    """
    Generate a video gallery web page using the supplied config.
    """
    config = config_item.read_as_config()
    video_gallery = as_dataclass(config, VideoGallery)  # Checks the format.

    content = render_web_template(
        media_templates_dir,
        "youtube_gallery.html.jinja",
        asdict(video_gallery),
    )

    return render_web_template(
        base_templates_dir,
        "base_webpage.html.jinja",
        {"title": video_gallery.title, "content": content},
    )
