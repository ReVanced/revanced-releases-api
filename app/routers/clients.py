from fastapi_paseto_auth import AuthPASETO
from fastapi import APIRouter, Request, Response, Depends, status, HTTPException
from app.dependencies import load_config
from app.controllers.Clients import Clients
import app.models.ClientModels as ClientModels
import app.models.ResponseModels as ResponseModels
import app.models.GeneralErrors as GeneralErrors
from app.utils.Generators import Generators

router = APIRouter(
    prefix="/client",
    tags=['Clients']
)
generators = Generators()
clients = Clients()
config: dict = load_config()

@router.post('/', response_model=ClientModels.ClientModel, status_code=status.HTTP_201_CREATED)
async def create_client(request: Request, response: Response, admin: bool | None = False, Authorize: AuthPASETO = Depends()) -> ClientModels.ClientModel:
    """Create a new API client.

    Returns:
        json: client information
    """
    
    Authorize.paseto_required()
    
    admin_claim: dict[str, bool] = {"admin": False}
    
    current_user: str | int | None = Authorize.get_subject()

    if 'admin' in Authorize.get_token_payload():
        admin_claim = {"admin": Authorize.get_token_payload()['admin']}
    
    if ( await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()) and 
        admin_claim['admin'] == True):
        
        client: ClientModels.ClientModel =  await clients.generate(admin=admin)
        await clients.store(client)
        
        return client
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )
    

@router.delete('/{client_id}', response_model=ResponseModels.ClientDeletedResponse, status_code=status.HTTP_200_OK)
async def delete_client(request: Request, response: Response, client_id: str, Authorize: AuthPASETO = Depends()) -> dict:
    """Delete an API client.

    Returns:
        json: deletion status
    """
    
    Authorize.paseto_required()
    
    admin_claim: dict[str, bool] = {"admin": False}
    
    current_user: str | int | None = Authorize.get_subject()

    if 'admin' in Authorize.get_token_payload():
        admin_claim = {"admin": Authorize.get_token_payload()['admin']}
        
    if ( await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()) and 
        ( admin_claim['admin'] == True or 
         current_user == client_id ) ):
        
        if await clients.exists(client_id):
            return {"id": client_id, "deleted": await clients.delete(client_id)}
        else:
            raise HTTPException(status_code=404, detail={
                "error": GeneralErrors.ClientNotFound().error,
                "message": GeneralErrors.ClientNotFound().message
                }
                                )
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )

@router.patch('/{client_id}/secret', response_model=ResponseModels.ClientSecretUpdatedResponse, status_code=status.HTTP_200_OK)
async def update_client(request: Request, response: Response, client_id: str, Authorize: AuthPASETO = Depends()) -> dict:
    """Update an API client's secret.

    Returns:
        json: client ID and secret
    """
    
    Authorize.paseto_required()
    
    admin_claim: dict[str, bool] = {"admin": False}
    
    current_user: str | int | None = Authorize.get_subject()

    if 'admin' in Authorize.get_token_payload():
        admin_claim = {"admin": Authorize.get_token_payload()['admin']}
        
    if ( await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()) and 
        ( admin_claim['admin'] == True or 
         current_user == client_id ) ):
        
        if await clients.exists(client_id):
            new_secret: str = await generators.generate_secret()
            
            if await clients.update_secret(client_id, new_secret):
                return {"id": client_id, "secret": new_secret}
            else: 
                raise HTTPException(status_code=500, detail={
                    "error": GeneralErrors.InternalServerError().error,
                    "message": GeneralErrors.InternalServerError().message
                    }
                                    )
        else:
            raise HTTPException(status_code=404, detail={
                "error": GeneralErrors.ClientNotFound().error,
                "message": GeneralErrors.ClientNotFound().message
                }
                                )
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )

@router.patch('/{client_id}/status', response_model=ResponseModels.ClientStatusResponse, status_code=status.HTTP_200_OK)
async def client_status(request: Request, response: Response, client_id: str, active: bool, Authorize: AuthPASETO = Depends()) -> dict:
    """Activate or deactivate a client

    Returns:
        json: json response containing client ID and activation status
    """
    
    Authorize.paseto_required()
    
    admin_claim: dict[str, bool] = {"admin": False}
    
    current_user: str | int | None = Authorize.get_subject()

    if 'admin' in Authorize.get_token_payload():
        admin_claim = {"admin": Authorize.get_token_payload()['admin']}
        print("admin claim: ", admin_claim)
    if ( await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()) and 
        ( admin_claim['admin'] == True or 
         current_user == client_id ) ):
        print("client exists")
        if await clients.exists(client_id):
            if await clients.status(client_id, active):
                return {"id": client_id, "active": active}
            else: 
                raise HTTPException(status_code=500, detail={
                    "error": GeneralErrors.InternalServerError().error,
                    "message": GeneralErrors.InternalServerError().message
                    }
                                    )
        else:
            print("Client does not exist")
            raise HTTPException(status_code=404, detail={
                "error": GeneralErrors.ClientNotFound().error,
                "message": GeneralErrors.ClientNotFound().message
                }
                                )
    else:
        raise HTTPException(status_code=401, detail={
            "error": GeneralErrors.Unauthorized().error,
            "message": GeneralErrors.Unauthorized().message
            }
                            )
