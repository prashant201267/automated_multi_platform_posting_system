import httpx

from app.config import settings
from app.platforms.base import BasePlatform, PlatformError

QUERY = """
mutation Publish($input: PublishPostInput!) {
  publishPost(input: $input) { post { url } }
}
"""


class HashnodePlatform(BasePlatform):
    name = "Hashnode"

    async def publish(self, message: str):
        if not settings.hashnode_token or not settings.hashnode_publication_id:
            raise PlatformError("Missing HASHNODE_TOKEN or HASHNODE_PUBLICATION_ID")
        variables = {"input": {
            "title": message[:80],
            "contentMarkdown": message,
            "publicationId": settings.hashnode_publication_id,
        }}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://gql.hashnode.com",
                json={"query": QUERY, "variables": variables},
                headers={"Authorization": settings.hashnode_token},
            )
        self.check(r)
        data = r.json()
        if data.get("errors"):
            raise PlatformError(data["errors"][0].get("message", "GraphQL error"))
        return data["data"]["publishPost"]["post"]["url"], True
