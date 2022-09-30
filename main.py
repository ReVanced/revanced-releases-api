#!/usr/bin/env python3

import toml
import sentry_sdk

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse, JSONResponse

from slowapi.util import get_remote_address
from slowapi import Limiter, _rate_limit_exceeded_handler

from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from slowapi.errors import RateLimitExceeded
from fastapi_cache.backends.redis import RedisBackend

from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.gnu_backtrace import GnuBacktraceIntegration

from modules.Releases import Releases
from modules.Clients import Clients
from modules.Announcements import Announcements

from modules.utils.Generators import Generators
from modules.utils.RedisConnector import RedisConnector

import modules.models.ClientModels as ClientModels
import modules.models.GeneralErrors as GeneralErrors
import modules.models.ResponseModels as ResponseModels
import modules.models.AnnouncementModels as AnnouncementModels

import modules.utils.Logger as Logger

# Enable sentry logging

# sentry_sdk.init(os.environ['SENTRY_DSN'], traces_sample_rate=1.0, integrations=[
#         RedisIntegration(),
#         HttpxIntegration(),
#         GnuBacktraceIntegration(),
#     ],)

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
                            })

# Slowapi limiter

limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup cache

@cache()
async def get_cache() -> int:
    return 1

# Routes

@app.get("/", response_class=RedirectResponse, status_code=status.HTTP_301_MOVED_PERMANENTLY, tags=['Root'])
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
async def create_client(request: Request, response: Response, admin: bool | None = False) -> ClientModels.ClientModel | dict:
    """Create a new API client.

    Returns:
        json: client information
    """
    new_client =  await clients.generate(admin=admin)
    try:
        await clients.store(new_client)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Internal server error",
                "message": "Database error"}
    return new_client

@app.delete('/client/{client_id}', response_model=ClientModels.ClientDeleted, status_code=status.HTTP_200_OK, tags=['Clients'])
@limiter.limit(config['slowapi']['limit'])
async def delete_client(request: Request, response: Response, client_id: str = None, responses={
    500: {"model: GeneralErrors.InternalServerError"},
    404: {"model: GeneralErrors.ItemNotFound"},
    400: {"model: GeneralErrors.IdNotProvided"}
    }
                       ) -> dict | JSONResponse:
    """Delete an API client.

    Returns:
        json: deletion status
    """
    
    if not client_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Bad request",
                "message": "Missing client id"}
        
    if await clients.exists(client_id):
        try:
            deleted = await clients.delete(client_id)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
        return {"id": client_id, "deleted": deleted}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Client not found"})

@app.patch('/client/{client_id}', response_model=ClientModels.ClientSecret, status_code=status.HTTP_200_OK, tags=['Clients'])
@limiter.limit(config['slowapi']['limit'])
async def update_client(request: Request, response: Response, client_id: str = None, responses={
    500: {"model: GeneralErrors.InternalServerError"},
    404: {"model: GeneralErrors.ItemNotFound"},
    400: {"model: GeneralErrors.IdNotProvided"}
    }
                       ) -> dict | JSONResponse:
    """Update an API client's secret.

    Returns:
        json: client ID and secret
    """
    if not client_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Bad request",
                "message": "Missing client id"}
        
    if await clients.exists(client_id):
        try:
            new_secret = await generators.generate_secret()
            updated = await clients.update_secret(client_id, new_secret)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
        if updated:
            return {"id": client_id, "new_secret": new_secret}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Not found", "id": client_id})

@app.post('/announcement', response_model=AnnouncementModels.AnnouncementCreatedResponse, status_code=status.HTTP_200_OK, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
async def create_announcement(request: Request, response: Response, announcement: AnnouncementModels.AnnouncementCreateModel, responses={
    500: {"model: GeneralErrors.InternalServerError"},
    }
                              ) -> dict | JSONResponse:
    """Create a new announcement.

    Returns:
        json: announcement information
    """
    try:
        announcement_created: bool = await announcements.store(announcement)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
    return {"created": announcement_created}

@app.get('/announcement/', response_model=AnnouncementModels.AnnouncementModel, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
async def get_announcement(request: Request, response: Response, responses={
    500: {"model: GeneralErrors.InternalServerError"},
    404: {"model: GeneralErrors.ItemNotFound"},
    400: {"model: GeneralErrors.IdNotProvided"}
    }
                          ) -> JSONResponse | dict:
    """Get an announcement.

    Returns:
        json: announcement information
    """
    if await announcements.exists():
        try:
            announcement = await announcements.get()
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
        if not announcement:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Not found"})
    return announcement

@app.delete('/announcement/', response_model=AnnouncementModels.AnnouncementDeleted, status_code=status.HTTP_200_OK, tags=['Announcements'])
@limiter.limit(config['slowapi']['limit'])
async def delete_announcement(request: Request, response: Response, responses={
    500: {"model: GeneralErrors.InternalServerError"},
    404: {"model: GeneralErrors.ItemNotFound"},
    400: {"model: GeneralErrors.IdNotProvided"}
    }
                       ) -> dict | JSONResponse:
    """Delete an announcement.

    Returns:
        json: deletion status
    """
       
    if await announcements.exists():
        try:
            deleted = await announcements.delete()
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})
        return {"deleted": deleted}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Client not found"})

@app.head('/ping', status_code=status.HTTP_204_NO_CONTENT, tags=['Misc'])
@limiter.limit(config['slowapi']['limit'])
async def ping(request: Request, response: Response) -> None:
    """Check if the API is running.

    Returns:
        None
    """
    return None

@app.on_event("startup")
async def startup() -> None:
    FastAPICache.init(RedisBackend(RedisConnector.connect(config['cache']['database'])), prefix="fastapi-cache")
    
    return None

# setup right before running to make sure no other library overwrites it

Logger.setup_logging(LOG_LEVEL=config["logging"]["level"], JSON_LOGS=config["logging"]["json_logs"])