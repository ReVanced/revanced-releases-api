from pydantic import BaseModel

class ClientModel(BaseModel):
    """Implements the fields for the clients.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    secret: str
    admin: bool
    active: bool

class ClientAuthModel(BaseModel):
    """Implements the fields for client authentication.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    secret: str
    
