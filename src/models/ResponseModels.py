from pydantic import BaseModel
import src.models.ResponseFields as ResponseFields

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
