from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import is_url_item
from kash.media_base.media_services import canonicalize_media_url, list_channel_items
from kash.model import NO_ARGS, ActionInput, ActionResult, Item
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


@kash_action(
    expected_args=NO_ARGS,
    precondition=is_url_item,
)
def list_channel(input: ActionInput) -> ActionResult:
    """
    List the contents of a media channel (YouTube, Apple Podcasts, etc.) channel, saving
    the URL of every audio or video as a resource item. Only adds the resources.
    Does not download any media.
    """
    item = input.items[0]
    if not item.url:
        raise InvalidInput("Item must have a URL")
    if not canonicalize_media_url(item.url):
        raise InvalidInput("Media format not supported")

    metadata_list = list_channel_items(item.url)

    result_items = []
    for metadata in metadata_list:
        if not canonicalize_media_url(metadata.url):
            log.warning("Skipping non-recognized video URL: %s", metadata.url)
            continue

        item = Item.from_media_metadata(metadata)
        result_items.append(item)

    return ActionResult(result_items)
