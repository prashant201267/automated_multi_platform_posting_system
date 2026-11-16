import asyncio

import httpx
import pytest

from app.config import settings
from app.platforms import get_platforms
from app.platforms import bluesky, devto, hashnode, mastodon, telegram

MSG = "Hello https://example.com"


REAL_CLIENT = httpx.AsyncClient


def mock_http(monkeypatch, module, handler):
    real = REAL_CLIENT
    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        lambda **kw: real(transport=httpx.MockTransport(handler), **kw),
    )


def run(platform):
    return asyncio.run(platform.post(MSG))


def test_all_platforms_fail_gracefully_without_credentials():
    for p in get_platforms():
        r = run(p)
        assert r.status == "failed" and "Missing" in r.error


def test_devto_success_and_http_error(monkeypatch):
    monkeypatch.setattr(settings, "devto_api_key", "k")
    mock_http(monkeypatch, devto, lambda req: httpx.Response(201, json={"url": "https://dev.to/a/1"}))
    r = run(devto.DevToPlatform())
    assert (r.status, r.posted_url, r.public_access) == ("success", "https://dev.to/a/1", True)
    mock_http(monkeypatch, devto, lambda req: httpx.Response(401, text="unauthorized"))
    r = run(devto.DevToPlatform())
    assert r.status == "failed" and "401" in r.error and r.posted_url is None


def test_mastodon_success(monkeypatch):
    monkeypatch.setattr(settings, "mastodon_access_token", "t")
    mock_http(monkeypatch, mastodon, lambda req: httpx.Response(200, json={"url": "https://m.s/1", "visibility": "public"}))
    r = run(mastodon.MastodonPlatform())
    assert r.status == "success" and r.public_access is True


def test_bluesky_success_with_link_facet(monkeypatch):
    monkeypatch.setattr(settings, "bluesky_handle", "me.bsky.social")
    monkeypatch.setattr(settings, "bluesky_app_password", "pw")
    seen = {}

    def handler(req):
        if req.url.path.endswith("createSession"):
            return httpx.Response(200, json={"did": "did:plc:x", "accessJwt": "j", "handle": "me.bsky.social"})
        seen["body"] = req.read().decode()
        return httpx.Response(200, json={"uri": "at://did:plc:x/app.bsky.feed.post/abc"})

    mock_http(monkeypatch, bluesky, handler)
    r = run(bluesky.BlueskyPlatform())
    assert r.posted_url == "https://bsky.app/profile/me.bsky.social/post/abc"
    assert "byteStart" in seen["body"]


def test_telegram_public_and_private(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "t")
    monkeypatch.setattr(settings, "telegram_channel", "@c")
    mock_http(monkeypatch, telegram, lambda req: httpx.Response(200, json={"result": {"message_id": 5, "chat": {"username": "c"}}}))
    r = run(telegram.TelegramPlatform())
    assert r.posted_url == "https://t.me/c/5" and r.public_access is True
    mock_http(monkeypatch, telegram, lambda req: httpx.Response(200, json={"result": {"message_id": 5, "chat": {}}}))
    assert run(telegram.TelegramPlatform()).public_access is False


def test_hashnode_success_and_graphql_error(monkeypatch):
    monkeypatch.setattr(settings, "hashnode_token", "t")
    monkeypatch.setattr(settings, "hashnode_publication_id", "p")
    ok = {"data": {"publishPost": {"post": {"url": "https://h.dev/p"}}}}
    mock_http(monkeypatch, hashnode, lambda req: httpx.Response(200, json=ok))
    assert run(hashnode.HashnodePlatform()).posted_url == "https://h.dev/p"
    mock_http(monkeypatch, hashnode, lambda req: httpx.Response(200, json={"errors": [{"message": "bad"}]}))
    r = run(hashnode.HashnodePlatform())
    assert r.status == "failed" and r.error == "bad"


def test_network_exception_is_captured(monkeypatch):
    monkeypatch.setattr(settings, "devto_api_key", "k")

    def boom(req):
        raise httpx.ConnectError("down")

    mock_http(monkeypatch, devto, boom)
    r = run(devto.DevToPlatform())
    assert r.status == "failed" and "down" in r.error
