from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Atlassian Admin Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Atlassian Cloud credentials
    ATLASSIAN_DOMAIN: str = ""  # e.g. "yoursite.atlassian.net"
    ATLASSIAN_EMAIL: str = ""
    ATLASSIAN_API_TOKEN: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Scheduler
    SYNC_INTERVAL_MINUTES: int = 60

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    @property
    def atlassian_base_url(self) -> str:
        return f"https://{self.ATLASSIAN_DOMAIN}"

    @property
    def jira_rest_url(self) -> str:
        return f"{self.atlassian_base_url}/rest/api/3"

    @property
    def confluence_rest_url(self) -> str:
        return f"{self.atlassian_base_url}/wiki/rest/api"

    @property
    def jsm_rest_url(self) -> str:
        return f"{self.atlassian_base_url}/rest/servicedeskapi"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
