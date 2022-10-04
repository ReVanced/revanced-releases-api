from pydantic import BaseModel

class InternalServerError(BaseModel):
    """Implements the response fields for when an internal server error occurs.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str = "Internal Server Error"
    message: str = "An internal server error occurred. Please try again later."
    
class AnnouncementNotFound(BaseModel):
    """Implements the response fields for when an item is not found.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str = "Not Found"
    message: str = "No announcement was found."
    
class ClientNotFound(BaseModel):
    """Implements the response fields for when a client is not found.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str = "Not Found"
    message: str = "No client matches the given ID"

class IdNotProvided(BaseModel):
    """Implements the response fields for when the id is not provided.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str = "Bad Request"
    message: str = "Missing client id"
    
class Unauthorized(BaseModel):
    """Implements the response fields for when the client is unauthorized.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    error: str = "Unauthorized"
    message: str = "The client is unauthorized to access this resource"