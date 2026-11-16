import asyncio

from app.platforms import get_platforms
from app.schemas import PlatformResult, PostingResponse


async def publish_everywhere(message: str, platforms=None) -> PostingResponse:
    platforms = platforms if platforms is not None else get_platforms()
    raw = await asyncio.gather(*(p.post(message) for p in platforms), return_exceptions=True)
    results = []
    for p, r in zip(platforms, raw):
        if isinstance(r, BaseException):
            r = PlatformResult(platform=p.name, status="failed", error=str(r) or r.__class__.__name__)
        results.append(r)
    return PostingResponse(success=any(r.status == "success" for r in results), results=results)
