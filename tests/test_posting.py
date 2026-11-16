from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import BasePlatform, PlatformError
from app.services import posting_service

client = TestClient(app)


class OkPlatform(BasePlatform):
    name = "Ok"

    async def publish(self, message):
        return "https://example.com/post/1", True


class FailPlatform(BasePlatform):
    name = "Fail"

    async def publish(self, message):
        raise PlatformError("Authentication failed")


def test_invalid_inputs():
    for msg in [
        "no link here",
        "two https://a.com and https://b.com",
        "bad link https://nodot",
        "x" * 201 + " https://example.com",
    ]:
        assert client.post("/posting", json={"message": msg}).status_code == 422


def test_partial_failure(monkeypatch):
    monkeypatch.setattr(posting_service, "get_platforms", lambda: [OkPlatform(), FailPlatform()])
    r = client.post("/posting", json={"message": "Hello https://example.com"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert [x["status"] for x in body["results"]] == ["success", "failed"]
    assert body["results"][1]["error"] == "Authentication failed"
    assert body["results"][0]["date"] and body["results"][0]["time"]
