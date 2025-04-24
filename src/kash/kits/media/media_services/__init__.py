from kash.kits.media.media_services.apple_podcasts import ApplePodcasts
from kash.kits.media.media_services.vimeo import Vimeo
from kash.kits.media.media_services.youtube import YouTube
from kash.media_base.media_services import register_media_service

youtube = YouTube()
vimeo = Vimeo()
apple_podcasts = ApplePodcasts()


register_media_service(youtube, vimeo, apple_podcasts)
