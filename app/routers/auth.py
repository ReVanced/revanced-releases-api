from fastapi_paseto_auth import AuthPASETO
from fastapi import APIRouter, Request, Response, Depends, status, HTTPException
from app.dependencies import load_config
from app.controllers.Clients import Clients
import app.models.ClientModels as ClientModels
import app.models.GeneralErrors as GeneralErrors
import app.models.ResponseModels as ResponseModels

router = APIRouter()
clients = Clients()
config: dict = load_config()

@router.post('/auth', response_model=ResponseModels.ClientAuthTokenResponse, status_code=status.HTTP_200_OK, tags=['Authentication'])
async def auth(request: Request, response: Response, client: ClientModels.ClientAuthModel, Authorize: AuthPASETO = Depends()) -> dict:
    """Authenticate a client and get an auth token.

    Returns:
        access_token: auth token
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
            
            return {"access_token": access_token}
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )