#!/usr/bin/env python3

import os
import toml
import sentry_sdk

from fastapi import FastAPI, Request, Response, status,  HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse, UJSONResponse

from slowapi.util import get_remote_address
from slowapi import Limiter, _rate_limit_exceeded_handler

from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from slowapi.errors import RateLimitExceeded
from fastapi_cache.backends.redis import RedisBackend

from fastapi_paseto_auth import AuthPASETO
from fastapi_paseto_auth.exceptions import AuthPASETOException

from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.gnu_backtrace import GnuBacktraceIntegration

import src.controllers.Auth as Auth
from src.controllers.Releases import Releases
from src.controllers.Clients import Clients
from src.controllers.Announcements import Announcements

from src.utils.Generators import Generators
from src.utils.RedisConnector import RedisConnector

import src.models.ClientModels as ClientModels
import src.models.GeneralErrors as GeneralErrors
import src.models.ResponseModels as ResponseModels
import src.models.AnnouncementModels as AnnouncementModels

import src.utils.Logger as Logger

# Enable sentry logging

sentry_sdk.init(os.environ['SENTRY_DSN'], traces_sample_rate=1.0, integrations=[
        RedisIntegration(),
        HttpxIntegration(),
        GnuBacktraceIntegration(),
    ],)

"""Get latest ReVanced releases from GitHub API."""

# Load config

config: dict = toml.load("config.toml")

# Class instances

generators = Generators()

releases = Releases()

clients = Clients()

announcements = Announcements()

# Create FastAPI instance

app = FastAPI(title=config['docs']['title'],
              description=config['docs']['description'],
              version=config['docs']['version'],
              license_info={"name": config['license']['name'],
                            "url": config['license']['url']
                            },
              default_response_class=UJSONResponse
              )

# Slowapi limiter

limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup cache

@cache()
async def get_cache() -> int:
    return 1

# Setup PASETO

@AuthPASETO.load_config
def get_config():
    return Auth.PasetoSettings()

@app.exception_handler(AuthPASETOException)
def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

# Routes

@app.get("/", response_class=RedirectResponse,
         status_code=status.HTTP_301_MOVED_PERMANENTLY, tags=['Root'])
@limiter.limit(config['slowapi']['limit'])
async def root(request: Request, response: Response) -> RedirectResponse:
    """Brings up API documentation

    Returns:
        None: Redirects to /docs
    """
    return RedirectResponse(url="/docs")

@app.get('/tools', response_model=ResponseModels.ToolsResponseModel, tags=['ReVanced Tools'])
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def tools(request: Request, response: Response) -> dict:
    """Get patching tools' latest version.

    Returns:
        json: information about the patching tools' latest version
    """
    return await releases.get_latest_releases(config['app']['repositories'])

@app.get('/patches', response_model=ResponseModels.PatchesResponseModel, tags=['ReVanced Tools'])
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def patches(request: Request, response: Response) -> dict:
    """Get latest patches.

    Returns:
        json: list of latest patches
    """
    
    return await releases.get_patches_json()

@app.get('/contributors', response_model=ResponseModels.ContributorsResponseModel, tags=['ReVanced Tools'])
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def contributors(request: Request, response: Response) -> dict:
    """Get contributors.

    Returns:
        json: list of contributors
    """
    return await releases.get_contributors(config['app']['repositories'])

@app.post('/client', response_model=ClientModels.ClientModel, status_code=status.HTTP_201_CREATED, tags=['Clients'])
@limiter.limit(config['slowapi']['limit'])
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
    

@app.delete('/client/{client_id}', response_model=ResponseModels.ClientDeletedResponse, status_code=status.HTTP_200_OK, tags=['Clients'])
@limiter.limit(config['slowapi']['limit'])
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

@app.patch('/client/{client_id}/secret', response_model=ResponseModels.ClientSecretUpdatedResponse, status_code=status.HTTP_200_OK, tags=['Clients'])
@limiter.limit(config['slowapi']['limit'])
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

@app.patch('/client/{client_id}/status', response_model=ResponseModels.ClientStatusResponse, status_code=status.HTTP_200_OK, tags=['Clients'])
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
        
    if ( await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()) and 
        ( admin_claim['admin'] == True or 
         current_user == client_id ) ):
        
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
    

@app.post('/announcement', response_model=AnnouncementModels.AnnouncementCreatedResponse,
          status_code=status.HTTP_201_CREATED, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
async def create_announcement(request: Request, response: Response,
                              announcement: AnnouncementModels.AnnouncementCreateModel,
                              Authorize: AuthPASETO = Depends()) -> dict:
    """Create a new announcement.

    Returns:
        json: announcement information
    """
    Authorize.paseto_required()
    
    if await clients.auth_checks(Authorize.get_subject(), Authorize.get_jti()):
        announcement_created: bool = await announcements.store(announcement)
        
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

@app.get('/announcement', response_model=AnnouncementModels.AnnouncementModel, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
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

@app.delete('/announcement',
            response_model=AnnouncementModels.AnnouncementDeleted,
            status_code=status.HTTP_200_OK, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
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
        
@app.post('/auth', response_model=ResponseModels.ClientAuthTokenResponse, status_code=status.HTTP_200_OK, tags=['Authentication'])
@limiter.limit(config['slowapi']['limit'])
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

@app.post('/refresh', response_model=ResponseModels.ClientTokenRefreshResponse,
          status_code=status.HTTP_200_OK, tags=['Authentication'])
@limiter.limit(config['slowapi']['limit'])
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

@app.on_event("startup")
async def startup() -> None:
    FastAPICache.init(RedisBackend(RedisConnector.connect(config['cache']['database'])),
                      prefix="fastapi-cache")
    
    return None

# setup right before running to make sure no other library overwrites it

Logger.setup_logging(LOG_LEVEL=config["logging"]["level"],
                     JSON_LOGS=config["logging"]["json_logs"])