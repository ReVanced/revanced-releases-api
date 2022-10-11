from fastapi_paseto_auth import AuthPASETO
from fastapi import APIRouter, Request, Response, Depends, status, HTTPException
from app.dependencies import load_config
from app.controllers.Announcements import Announcements
from app.controllers.Clients import Clients
import app.models.AnnouncementModels as AnnouncementModels
import app.models.GeneralErrors as GeneralErrors

router = APIRouter(
    prefix="/announcement",
    tags=['Announcement']
)

clients = Clients()
announcements = Announcements()
config: dict = load_config()

@router.post('/', response_model=AnnouncementModels.AnnouncementCreatedResponse,
          status_code=status.HTTP_201_CREATED)
async def create_announcement(request: Request, response: Response,
                              announcement: AnnouncementModels.AnnouncementCreateModel,
                              Authorize: AuthPASETO = Depends()) -> dict:
    """Create a new announcement.

    Returns:
        json: announcement information
    """
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):
        announcement_created: bool = await announcements.store(announcement=announcement,
                                                               author=Authorize.get_subject())
        
        if announcement_created:
            return {"created": announcement_created}
        else:
            raise HTTPException(status_code=500, detail={
                "error": GeneralErrors.InternalServerError().error,
                "message": GeneralErrors.InternalServerError().message
                }
                                )
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )

@router.get('/', response_model=AnnouncementModels.AnnouncementModel)
async def get_announcement(request: Request, response: Response) -> dict:
    """Get an announcement.

    Returns:
        json: announcement information
    """
    if await announcements.exists():
        return await announcements.get()
    else:
        raise HTTPException(status_code=404, detail={
            "error": GeneralErrors.AnnouncementNotFound().error,
            "message": GeneralErrors.AnnouncementNotFound().message
            }
                            )

@router.delete('/',
            response_model=AnnouncementModels.AnnouncementDeleted,
            status_code=status.HTTP_200_OK)
async def delete_announcement(request: Request, response: Response,
                              Authorize: AuthPASETO = Depends()) -> dict:
    """Delete an announcement.

    Returns:
        json: deletion status
    """
    
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):   
        if await announcements.exists():
            return {"deleted": await announcements.delete()}
        else:
            raise HTTPException(status_code=404, detail={
                "error": GeneralErrors.AnnouncementNotFound().error,
                "message": GeneralErrors.AnnouncementNotFound().message
                }
                                )
    else: 
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )
