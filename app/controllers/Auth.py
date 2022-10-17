import os
import toml
from pydantic import BaseModel

config: dict = toml.load("config.toml")

class PasetoSettings(BaseModel):
    authpaseto_secret_key: str = os.environ['SECRET_KEY']
    authpaseto_access_token_expires: int | bool = config['auth']['access_token_expires']
    