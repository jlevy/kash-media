from kash.exec.precondition_registry import kash_precondition
from kash.model.items_model import Item


@kash_precondition
def has_video_id(item: Item) -> bool:
    from kash.media_base.media_services import get_media_id

    return bool(item.url and get_media_id(item.url))


@kash_precondition
def is_youtube_video(item: Item) -> bool:
    from kash.kits.media.libs import youtube

    return bool(item.url and youtube.canonicalize(item.url))
