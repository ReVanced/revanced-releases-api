from datetime import timedelta
import os
import toml
from datetime import timedelta
from pydantic import BaseModel
from fastapi_paseto_auth import AuthPASETO

config: dict = toml.load("config.toml")

class PasetoSettings(BaseModel):
    authpaseto_secret_key: str = os.environ['SECRET_KEY']
    authpaseto_access_token_expires: int | bool = config['auth']['access_token_expires']
    authpaseto_denylist_enabled: bool = True
