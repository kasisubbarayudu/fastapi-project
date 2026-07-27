from typing import Optional
import boto3
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


# Define Pydantic schema for environments variables user has to export
class DBConfig(BaseSettings):
    db_host: str
    db_passwd: str
    access_token_expiry_period_in_minutes: int
    db_user: str = "postgres"
    db_name: str = "fastapi"
    cognito_region: Optional[str] = None
    cognito_user_pool_id: Optional[str] = None
    cognito_client_id: Optional[str] = None
    cognito_backend: bool = False

    model_config = SettingsConfigDict(
        env_file=".env")

config = DBConfig()

if config.cognito_backend:

    def initialise_boto3():
        cognito_idp_client = boto3.client(
            "cognito-idp", region_name=config.cognito_region
        )
        return cognito_idp_client
