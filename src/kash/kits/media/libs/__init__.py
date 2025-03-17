from pathlib import Path

from kash.kits.media.libs.services.apple_podcasts import ApplePodcasts
from kash.kits.media.libs.services.vimeo import Vimeo
from kash.kits.media.libs.services.youtube import YouTube
from kash.media_base.media_services import register_media_service

youtube = YouTube()
vimeo = Vimeo()
apple_podcasts = ApplePodcasts()


register_media_service(youtube, vimeo, apple_podcasts)


media_templates_dir = Path(__file__).parent / "templates"
"""Media-related templates."""
