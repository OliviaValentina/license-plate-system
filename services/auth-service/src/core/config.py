from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    API_V1_STR: str = "/auth/v1"
    PROJECT_NAME: str = "Authentication_Service"

    # Logging
    LOG_LEVEL: str = "INFO"

    # JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SECRET_KEY: str

    # Active Directory
    DOMAIN_NAME: str
    DOMAIN_LOCAL: str
    SERVER_IP: str
    AD_CONNECT_TIMEOUT_SECONDS: int = 5
    AD_RECEIVE_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"   # <-- THIS loads your .env automatically
        env_file_encoding = "utf-8"

    @computed_field
    def DN(self) -> str:
        return f"{self.DOMAIN_NAME}.{self.DOMAIN_LOCAL}" # DN: Domain name, eg.: name.at


settings = Settings()
