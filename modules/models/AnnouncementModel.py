from pydantic import BaseModel

class AnnouncementModel(BaseModel):
    """Implements the fields for the announcements.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    id: str
    timestamp: str
    owner: str
    title: str
    content: str