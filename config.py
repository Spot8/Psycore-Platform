from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET = "dev-only-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg2://aegisflo:aegisflo@localhost:5432/aegisflo"
    secret_key: str = DEFAULT_SECRET
    access_token_minutes: int = 60
    auth_mode: str = "mock"  # mock | oidc
    cors_origins: str = "http://localhost:3000"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    oidc_email_claim: str = "email"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def validate_runtime(self) -> None:
        """Fail fast on unsafe configuration."""
        if self.auth_mode not in ("mock", "oidc"):
            raise RuntimeError("AUTH_MODE must be 'mock' or 'oidc'")
        if self.auth_mode == "oidc" and not (
            self.oidc_issuer and self.oidc_audience and self.oidc_jwks_url
        ):
            raise RuntimeError("OIDC_ISSUER, OIDC_AUDIENCE and OIDC_JWKS_URL are required for AUTH_MODE=oidc")
        if self.environment == "production":
            if self.auth_mode == "mock":
                raise RuntimeError("AUTH_MODE=mock is not allowed when ENVIRONMENT=production")
            if self.secret_key == DEFAULT_SECRET or len(self.secret_key) < 32:
                raise RuntimeError("SECRET_KEY must be a unique value of at least 32 characters in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
