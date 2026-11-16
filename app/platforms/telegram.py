import httpx

from app.config import settings
from app.platforms.base import BasePlatform, PlatformError


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    async def publish(self, message: str):
        if not settings.telegram_bot_token or not settings.telegram_channel:
            raise PlatformError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL")
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": settings.telegram_channel, "text": message},
            )
        self.check(r)
        result = r.json()["result"]
        username = result["chat"].get("username")
        if not username:
            return f"telegram:message_id={result['message_id']}", False
        return f"https://t.me/{username}/{result['message_id']}", True
