from fastapi_paseto_auth import AuthPASETO
from fastapi import APIRouter, Request, Response, Depends, status, HTTPException
from app.dependencies import load_config
from fastapi_cache.decorator import cache
from app.controllers.Clients import Clients
from app.controllers.Mirrors import Mirrors
import app.models.MirrorModels as MirrorModels
import app.models.GeneralErrors as GeneralErrors

router = APIRouter(
    prefix="/mirrors",
    tags=['CDN Mirrors']
)

clients = Clients()
mirrors = Mirrors()

config: dict = load_config()

@router.get('/{org}/{repo}/{version}', status_code=status.HTTP_200_OK, response_model=MirrorModels.MirrorModel)
async def get_mirrors(request: Request, response: Response, org: str, repo: str, version: str) -> MirrorModels.MirrorModel:
    """Get CDN mirror information for a given release.
    
    Returns:
        json: mirror information
    """
    
    if not await mirrors.exists(org, repo, version):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": GeneralErrors.MirrorNotFoundError().error,
            "message": GeneralErrors.MirrorNotFoundError().message
            }
                            )
    else:
        return await mirrors.get(org, repo, version)

@router.post('/{org}/{repo}/{version}', status_code=status.HTTP_201_CREATED, response_model=MirrorModels.MirrorCreatedResponseModel)
async def create_mirror(request: Request, response: Response, org: str, repo: str, version: str,
                        mirror: MirrorModels.MirrorStoreModel, Authorize: AuthPASETO = Depends()) -> dict:
    """Stores information about a new CDN mirror for a given release.
    
    Returns:
        bool: True if successful, False otherwise
    """
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):
        if await mirrors.exists(org, repo, version):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
                "error": GeneralErrors.MirrorAlreadyExistsError().error,
                "message": GeneralErrors.MirrorAlreadyExistsError().message
                }
                                )
        else:
            key = await mirrors.assemble_key(org, repo, version)
            created: bool = await mirrors.store(org, repo, version, mirror)
            if created:
                return {"created": created, "key": key}
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
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

@router.put('/{org}/{repo}/{version}', status_code=status.HTTP_200_OK, response_model=MirrorModels.MirrorUpdatedResponseModel)
async def update_mirror(request: Request, response: Response, org: str, repo: str, version: str,
                        mirror: MirrorModels.MirrorStoreModel,Authorize: AuthPASETO = Depends()) -> dict:
    """Updates a stored information about CDN mirrors for a given release
    
    Returns:
        bool: True if successful, False otherwise
    """
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):
        if not await mirrors.exists(org, repo, version):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                "error": GeneralErrors.MirrorNotFoundError().error,
                "message": GeneralErrors.MirrorNotFoundError().message
                }
                                )
        else:
            key = await mirrors.assemble_key(org, repo, version)
            updated: bool = await mirrors.store(org, repo, version, mirror)
            if updated:
                return {"updated": updated, "key": key}
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
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

@router.delete('/{org}/{repo}/{version}', status_code=status.HTTP_200_OK, response_model=MirrorModels.MirrorDeletedResponseModel)
async def delete_mirror(request: Request, response: Response, org: str, repo: str, version: str, Authorize: AuthPASETO = Depends()) -> dict:
    """Deletes a stored information about CDN mirrors for a given release
    
    Returns:
        json: _description_
    """
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):
        if not await mirrors.exists(org, repo, version):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                "error": GeneralErrors.MirrorNotFoundError().error,
                "message": GeneralErrors.MirrorNotFoundError().message
                }
                                )
        else:
            key = await mirrors.assemble_key(org, repo, version)
            deleted: bool = await mirrors.delete(org, repo, version)
            if deleted:
                return {"deleted": deleted, "key": key}
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
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