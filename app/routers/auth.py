from fastapi_paseto_auth import AuthPASETO
from fastapi import APIRouter, Request, Response, Depends, status, HTTPException
from app.dependencies import load_config
from app.controllers.Clients import Clients
import app.models.ClientModels as ClientModels
import app.models.GeneralErrors as GeneralErrors
import app.models.ResponseModels as ResponseModels

router = APIRouter(
    prefix="/auth",
    tags=['Authentication']
)
clients = Clients()
config: dict = load_config()

@router.post('/', response_model=ResponseModels.ClientAuthTokenResponse, status_code=status.HTTP_200_OK)
async def auth(request: Request, response: Response, client: ClientModels.ClientAuthModel, Authorize: AuthPASETO = Depends()) -> dict:
    """Authenticate a client and get an auth token.

    Returns:
        access_token: auth token
        refresh_token: refresh token
    """
    
    admin_claim: dict[str, bool]
    
    if await clients.exists(client.id):
        authenticated: bool = await clients.authenticate(client.id, client.secret)
        
        if not authenticated:
            raise HTTPException(status_code=401, detail={
                "error": GeneralErrors.Unauthorized().error,
                "message": GeneralErrors.Unauthorized().message
                }
                                )
        else:
            if await clients.is_admin(client.id):
                admin_claim = {"admin": True}
            else:
                admin_claim = {"admin": False}
                
            access_token = Authorize.create_access_token(subject=client.id,
                                                         user_claims=admin_claim,
                                                         fresh=True)
            
            refresh_token = Authorize.create_refresh_token(subject=client.id,
                                                           user_claims=admin_claim)
            
            return {"access_token": access_token, "refresh_token": refresh_token}
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )

@router.post('/refresh', response_model=ResponseModels.ClientTokenRefreshResponse,
          status_code=status.HTTP_200_OK, tags=['Authentication'])
async def refresh(request: Request, response: Response,
                  Authorize: AuthPASETO = Depends()) -> dict:
    """Refresh an auth token.
    
    Returns:
        access_token: auth token
    """
    
    Authorize.paseto_required(refresh_token=True)
    
    admin_claim: dict[str, bool] = {"admin": False}
    
    current_user: str | int | None = Authorize.get_subject()

    if 'admin' in Authorize.get_token_payload():
        admin_claim = {"admin": Authorize.get_token_payload()['admin']}
    
    return {"access_token": Authorize.create_access_token(subject=current_user,
                                                          user_claims=admin_claim,
                                                          fresh=False)}