from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas import PlatformResult


class PlatformError(Exception):
    pass


class BasePlatform(ABC):
    name: str = "base"

    @abstractmethod
    async def publish(self, message: str) -> tuple[str, bool]:
        """Publish the message and return (posted_url, public_access)."""

    async def post(self, message: str) -> PlatformResult:
        try:
            url, public = await self.publish(message)
            now = datetime.now()
            return PlatformResult(
                platform=self.name,
                status="success",
                posted_url=url,
                public_access=public,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
            )
        except Exception as exc:
            return PlatformResult(
                platform=self.name,
                status="failed",
                error=str(exc) or exc.__class__.__name__,
            )

    @staticmethod
    def check(resp) -> None:
        if resp.status_code >= 400:
            raise PlatformError(f"HTTP {resp.status_code}: {resp.text[:200]}")
