from pydantic import BaseModel
from typing import Literal

AnnouncementType = Literal["info", "warning", "error"]

class AnnouncementModel(BaseModel):
    """Implements the fields for the announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    created_at: int
    author: str
    type: AnnouncementType
    title: str
    content: str
    
class AnnouncementCreateModel(BaseModel):
    """Implements the fields for creating an announcement.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    type: AnnouncementType
    title: str
    content: str
    
class AnnouncementCreatedResponse(BaseModel):
    """Implements the response fields for created announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    created: bool
    
class AnnouncementDeleted(BaseModel):
    """Implements the response fields for deleted announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    deleted: bool
