from pydantic import BaseModel

class MirrorModel(BaseModel):
    """Implements the response fields for the CDN mirror.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    repository: str
    version: str
    cid: str
    filenames: list[str]
    
class MirrorStoreModel(BaseModel):
    """Implements the fields for storing CDN mirror information.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    cid: str
    filenames: list[str]
    
class MirrorCreatedResponseModel(BaseModel):
    """Implements the response fields for stored CDN mirrors.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    created: bool
    key: str
    
class MirrorUpdatedResponseModel(BaseModel):
    """Implements the response fields for updated CDN mirrors.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    updated: bool
    key: str
    
class MirrorDeletedResponseModel(BaseModel):
    """Implements the response fields for deleted CDN mirrors.
    
    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    deleted: bool
    key: str
