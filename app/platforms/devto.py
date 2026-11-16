import httpx

from app.config import settings
from app.platforms.base import BasePlatform, PlatformError


class DevToPlatform(BasePlatform):
    name = "Dev.to"

    async def publish(self, message: str):
        if not settings.devto_api_key:
            raise PlatformError("Missing DEVTO_API_KEY")
        payload = {"article": {"title": message[:80], "body_markdown": message, "published": True}}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://dev.to/api/articles",
                json=payload,
                headers={"api-key": settings.devto_api_key},
            )
        self.check(r)
        return r.json()["url"], True
