#!/usr/bin/env python3

import os

import binascii
from redis import Redis

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, UJSONResponse

from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler

from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from slowapi.errors import RateLimitExceeded
from fastapi_cache.backends.redis import RedisBackend

from fastapi_paseto_auth import AuthPASETO
from fastapi_paseto_auth.exceptions import AuthPASETOException

import app.controllers.Auth as Auth
from app.controllers.Clients import Clients

from app.utils.RedisConnector import RedisConnector

import app.models.GeneralErrors as GeneralErrors

from app.routers import root
from app.routers import ping
from app.routers import auth
from app.routers import tools
from app.routers import clients
from app.routers import patches
from app.routers import mirrors
from app.routers import socials
from app.routers import changelogs
from app.routers import contributors
from app.routers import announcement

from app.dependencies import load_config

"""Get latest ReVanced releases from GitHub API."""

# Load config

config: dict = load_config()

# Create FastAPI instance

app = FastAPI(title=config['docs']['title'],
              description=config['docs']['description'],
              version=config['docs']['version'],
              license_info={"name": config['license']['name'],
                            "url": config['license']['url']
                            },
              default_response_class=UJSONResponse
              )

# Hook up rate limiter
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[
                      config['slowapi']['limit']
                      ],
                  headers_enabled=True,
                  storage_uri=f"redis://{os.environ['REDIS_URL']}:{os.environ['REDIS_PORT']}/{config['slowapi']['database']}"
                  )
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Setup routes

app.include_router(root.router)
app.include_router(tools.router)
app.include_router(patches.router)
app.include_router(contributors.router)
app.include_router(changelogs.router)
app.include_router(socials.router)
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(announcement.router)
app.include_router(mirrors.router)
app.include_router(ping.router)

# Setup cache

@cache()
async def get_cache() -> int:
    """Get cache TTL from config.

    Returns:
        int: Cache TTL
    """
    return 1

# Setup PASETO

@AuthPASETO.load_config
def get_config() -> Auth.PasetoSettings:
    """Get PASETO config from Auth module

    Returns:
        PasetoSettings: PASETO config
    """
    return Auth.PasetoSettings()

@AuthPASETO.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    redis = Redis(host=os.environ['REDIS_URL'],
              port=os.environ['REDIS_PORT'],
              db=config['tokens']['database'],
              decode_responses=True)
    
    return redis.exists(decrypted_token["jti"])

# Setup custom error handlers

@app.exception_handler(AuthPASETOException)
async def authpaseto_exception_handler(request: Request, exc: AuthPASETOException) -> JSONResponse:
    """Handle AuthPASETOException

    Args:
        request (Request): Request
        exc (AuthPASETOException): Exception

    Returns:
        JSONResponse: Response
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.exception_handler(AttributeError)
async def validation_exception_handler(request, exc) -> JSONResponse:
    """Handle AttributeError

    Args:
        request (Request): Request
        exc (AttributeError): Exception

    Returns:
        JSONResponse: Response
    """
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={
        "error": "Unprocessable Entity"
        })

@app.exception_handler(binascii.Error)
async def invalid_token_exception_handler(request, exc) -> JSONResponse:
    """Handle binascii.Error

    Args:
        request (Request): Request
        exc (binascii.Error): Exception

    Returns:
        JSONResponse: Response
    """
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={
        "error": GeneralErrors.Unauthorized().error,
        "message": GeneralErrors.Unauthorized().message
        })

@app.on_event("startup")
async def startup() -> None:
    """Startup event handler"""
    
    clients = Clients()
    await clients.setup_admin()
    FastAPICache.init(RedisBackend(RedisConnector.connect(config['cache']['database'])),
                      prefix="fastapi-cache")
    
    return None
