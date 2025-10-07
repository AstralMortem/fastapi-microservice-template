from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class MicroserviceSettings(BaseSettings):
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    SERVICE_NAME: str = "Microservice"
    SERVICE_CODE: str = Field(
        default_factory=lambda e: e["SERVICE_NAME"].lower()
    )  # Used by message brokers

    # Routing
    GLOBAL_ROUTER_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 12  # 12 days

    ## RBAC
    ENABLE_RBAC: bool = True

    # DATABASE
    DATABASE_URL: PostgresDsn = ""
    DATABASE_ENGINE_PARAMS: dict = {}



settings = MicroserviceSettings()
