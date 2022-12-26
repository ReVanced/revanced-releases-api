from datetime import timedelta
import os

from datetime import timedelta
from pydantic import BaseModel
from fastapi_paseto_auth import AuthPASETO

from app.dependencies import load_config

config: dict = load_config()

class PasetoSettings(BaseModel):
    authpaseto_secret_key: str = os.environ['SECRET_KEY']
    authpaseto_access_token_expires: int | bool = config['auth']['access_token_expires']
    authpaseto_denylist_enabled: bool = True
