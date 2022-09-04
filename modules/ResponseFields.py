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
    
class ContributorFields(BaseModel):
    """Implements the fields for each contributor in the /contributors endpoint.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    login: str
    id: str
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: str
    contributions: int
    
class ContributorsResponseFields(BaseModel):
    """Implements the fields for each repository in the /contributors endpoint

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    name: str
    contributors: list[ ContributorFields ]