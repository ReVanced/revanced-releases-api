from pydantic import BaseModel
import app.models.ResponseFields as ResponseFields

"""Implements pydantic models and model generator for the API's responses."""

class ToolsResponseModel(BaseModel):
    """Implements the JSON response model for the /tools endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    tools: list[ ResponseFields.ToolsResponseFields ]

class PatchesResponseModel(BaseModel):
    """Implements the JSON response model for the /patches endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    __root__: list[ ResponseFields.PatchesResponseFields ]
    
class ContributorsResponseModel(BaseModel):
    """Implements the JSON response model for the /contributors endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    repositories: list[ ResponseFields.ContributorsResponseFields ]
    
class PingResponseModel(BaseModel):
    """Implements the JSON response model for the /heartbeat endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    status: int
    detail: str

class ClientDeletedResponse(BaseModel):
    """Implements the response fields for deleted clients.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    deleted: bool
    
class ClientSecretUpdatedResponse(BaseModel):
    """Implements the response fields for updated client secrets.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    secret: str

class ClientAuthTokenResponse(BaseModel):
    """Implements the response fields for client auth tokens.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    access_token: str

class ClientTokenRefreshResponse(BaseModel):
    """Implements the response fields for client token refresh.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    access_token: str

class ClientStatusResponse(BaseModel):
    """Implements the response fields for client status.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    active: bool
    
class ChangelogsResponseModel(BaseModel):
    """Implements the JSON response model for the /changelogs endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    repository: str
    path: str
    commits: list[ ResponseFields.ChangelogsResponseFields ]
    
class RevokedTokenResponse(BaseModel):
    """Implements the response fields for token invalidation.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    revoked: bool
