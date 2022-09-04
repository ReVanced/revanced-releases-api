import modules.ResponseFields as ResponseFields
from pydantic import BaseModel

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