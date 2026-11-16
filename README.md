# Automated Multi-Platform Posting

FastAPI app: `POST /posting` publishes a short message (max 200 chars, exactly one URL) to Dev.to, Mastodon, Bluesky, Telegram and Hashnode concurrently. A failure on one platform doesn't affect the others.

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
uvicorn app.main:app --host 0.0.0.0 --port 4000
```
Docs: http://localhost:4000/docs

## Credentials
- **Dev.to**: Settings > Extensions > generate API key -> `DEVTO_API_KEY`
- **Mastodon**: Preferences > Development > New application (write:statuses) -> `MASTODON_ACCESS_TOKEN`, `MASTODON_BASE_URL`
- **Bluesky**: Settings > App Passwords -> `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`
- **Telegram**: create a bot via @BotFather, make it admin of a public channel -> `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL` (e.g. `@mychannel`)
- **Hashnode**: Settings > Developer > Personal Access Token -> `HASHNODE_TOKEN`; publication id -> `HASHNODE_PUBLICATION_ID`

## Example
```bash
curl -X POST localhost:4000/posting -H "Content-Type: application/json" \
  -d '{"message": "Grow your visibility https://example.com"}'
```
Platforms with missing credentials report `failed` with an error message.

## Tests
```bash
pytest
```
