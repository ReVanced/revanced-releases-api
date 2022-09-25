from pydantic import BaseModel

class InternalServerError(BaseModel):
    """Implements the response fields for when an internal server error occurs.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str
    
class ItemNotFound(BaseModel):
    """Implements the response fields for when an item is not found.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str
    id: str
    
class IdNotProvided(BaseModel):
    """Implements the response fields for when the id is not provided.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str
    message: str