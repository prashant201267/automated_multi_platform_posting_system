import re
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
MAX_LENGTH = 200


def extract_url(message: str) -> str:
    return URL_PATTERN.search(message).group(0)


class PostingRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty")
        if len(v) > MAX_LENGTH:
            raise ValueError(f"Message must not exceed {MAX_LENGTH} characters")
        urls = URL_PATTERN.findall(v)
        if len(urls) != 1:
            raise ValueError("Message must contain exactly one CTA link")
        url = urls[0].rstrip(".,;:!?)")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or "." not in parsed.netloc:
            raise ValueError("Invalid URL in message")
        return v


class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostingResponse(BaseModel):
    success: bool
    results: List[PlatformResult]
