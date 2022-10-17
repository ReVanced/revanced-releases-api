from typing import Any
from pydantic import BaseModel

class ToolsResponseFields(BaseModel):
    """Implements the fields for the /tools endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    repository: str
    version: str
    timestamp: str
    name: str
    size: str | None = None
    browser_download_url: str
    content_type: str
class CompatiblePackagesResponseFields(BaseModel):
    """Implements the fields for compatible packages in the PatchesResponseFields class.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    name: str
    versions: list[ str ] | None

class PatchesOptionsResponseFields(BaseModel):
    key: str
    title: str
    description: str
    required: bool
    choices: list[ Any ] | None

class PatchesResponseFields(BaseModel):
    """Implements the fields for the /patches endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    name: str
    description: str
    version: str
    excluded: bool
    deprecated: bool
    dependencies: list[ str ] | None
    options: list[ PatchesOptionsResponseFields ] | None
    compatiblePackages: list[ CompatiblePackagesResponseFields ]
    
class ContributorFields(BaseModel):
    """Implements the fields for each contributor in the /contributors endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    login: str
    avatar_url: str
    html_url: str
    
class ContributorsResponseFields(BaseModel):
    """Implements the fields for each repository in the /contributors endpoint

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    name: str
    contributors: list[ ContributorFields ]
    
class ChangelogsResponseFields(BaseModel):
    """Implements the fields for the /changelogs endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    sha: str
    author: str
    message: str
    html_url: str
