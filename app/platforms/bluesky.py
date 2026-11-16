from datetime import datetime, timezone

import httpx

from app.config import settings
from app.platforms.base import BasePlatform, PlatformError
from app.schemas import URL_PATTERN

BASE = "https://bsky.social/xrpc"


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"

    async def publish(self, message: str):
        if not settings.bluesky_handle or not settings.bluesky_app_password:
            raise PlatformError("Missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD")
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{BASE}/com.atproto.server.createSession",
                json={"identifier": settings.bluesky_handle, "password": settings.bluesky_app_password},
            )
            self.check(r)
            session = r.json()

            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            m = URL_PATTERN.search(message)
            if m:
                start = len(message[: m.start()].encode("utf-8"))
                end = start + len(m.group(0).encode("utf-8"))
                record["facets"] = [{
                    "index": {"byteStart": start, "byteEnd": end},
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}],
                }]
            r = await client.post(
                f"{BASE}/com.atproto.repo.createRecord",
                json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
                headers={"Authorization": f"Bearer {session['accessJwt']}"},
            )
        self.check(r)
        rkey = r.json()["uri"].split("/")[-1]
        return f"https://bsky.app/profile/{session['handle']}/post/{rkey}", True
