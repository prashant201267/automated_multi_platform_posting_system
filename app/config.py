from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    devto_api_key: str = ""
    mastodon_base_url: str = "https://mastodon.social"
    mastodon_access_token: str = ""
    bluesky_handle: str = ""
    bluesky_app_password: str = ""
    telegram_bot_token: str = ""
    telegram_channel: str = ""
    hashnode_token: str = ""
    hashnode_publication_id: str = ""


settings = Settings()
