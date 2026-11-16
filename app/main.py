from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import publish_everywhere

app = FastAPI(title="Automated Multi-Platform Posting System")


@app.post("/posting", response_model=PostingResponse)
async def posting(request: PostingRequest):
    return await publish_everywhere(request.message)
