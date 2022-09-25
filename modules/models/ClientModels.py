from pydantic import BaseModel
class ClientModel(BaseModel):
    """Implements the fields for the clients.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    secret: str
    admin: bool
    
class ClientDeleted(BaseModel):
    """Implements the response fields for deleted clients.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    deleted: bool
    
class ClientSecret(BaseModel):
    """Implements the response fields for updated client secrets.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    new_secret: str
    
