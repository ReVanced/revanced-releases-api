from pydantic import BaseModel

class ToolsResponseFields(BaseModel):
    """Implements the fields for the /tools endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    repository: str
    name: str
    size: str
    browser_download_url: str
    content_type: str
class CompatiblePackagesResponseFields(BaseModel):
    """Implements the fields for compatible packages in the PatchesResponseFields class.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    name: str
    versions: list[ str ] | None
class PatchesResponseFields(BaseModel):
    """Implements the fields for the /patches endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    name: str
    description: str
    version: str
    excluded: bool
    dependencies: list[ str ] | None
    compatiblePackages: list[ CompatiblePackagesResponseFields ]