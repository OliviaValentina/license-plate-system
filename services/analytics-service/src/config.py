from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the Analytics Service"""

    # Database settings
    db_user: str = Field(..., alias='DB_USER')
    db_password: str = Field(..., alias='DB_PASSWORD')
    db_host: str = Field(..., alias='DB_HOST')
    db_port: int = Field(..., alias='DB_PORT')
    db_name: str = Field(..., alias='DB_NAME')
    analytics_schema: str = Field(..., alias='ANALYTICS_SCHEMA')
    data_collection_schema: str = Field(..., alias='DATA_COLLECTION_SCHEMA')

    # Service-specific settings
    log_level: str = Field('INFO', alias='LOG_LEVEL')
    refresh_interval_seconds: int = Field(3600, alias='ANALYTICS_REFRESH_INTERVAL_SECONDS')

    @property
    def db_uri(self) -> PostgresDsn:
        """Constructs the PostgreSQL connection URI."""
        return PostgresDsn.build(
            scheme='postgresql+psycopg2',
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            path=self.db_name,
        )


settings = Settings()
