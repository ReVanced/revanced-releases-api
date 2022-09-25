from pydantic import BaseModel

class AnnouncementModel(BaseModel):
    """Implements the fields for the announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    created_at: int
    updated_at: int
    owner: str
    title: str
    content: str
    
class AnnouncementCreateModel(BaseModel):
    """Implements the fields for creating an announcement.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    owner: str
    title: str
    content: str
    
class AnnouncementCreatedResponse(BaseModel):
    """Implements the response fields for created announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    
class AnnouncementDeleted(BaseModel):
    """Implements the response fields for deleted announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    deleted: bool