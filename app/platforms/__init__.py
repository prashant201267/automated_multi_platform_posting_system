from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.hashnode import HashnodePlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform


def get_platforms():
    return [
        DevToPlatform(),
        MastodonPlatform(),
        BlueskyPlatform(),
        TelegramPlatform(),
        HashnodePlatform(),
    ]
