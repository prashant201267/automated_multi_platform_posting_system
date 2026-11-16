import httpx

from app.config import settings
from app.platforms.base import BasePlatform, PlatformError


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def publish(self, message: str):
        if not settings.mastodon_access_token:
            raise PlatformError("Missing MASTODON_ACCESS_TOKEN")
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{settings.mastodon_base_url.rstrip('/')}/api/v1/statuses",
                data={"status": message, "visibility": "public"},
                headers={"Authorization": f"Bearer {settings.mastodon_access_token}"},
            )
        self.check(r)
        data = r.json()
        return data["url"], data.get("visibility") == "public"
