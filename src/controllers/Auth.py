import os
from pydantic import BaseModel

class PasetoSettings(BaseModel):
    authpaseto_secret_key: str = os.environ['SECRET_KEY']
    authpaseto_access_token_expires: int = 3600
    