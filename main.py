#!/usr/bin/env python3

import os
import toml #type: ignore
import uvicorn #type: ignore
import aioredis #type: ignore
from fastapi import FastAPI, Request, Response #type: ignore
from modules.Releases import Releases
from fastapi.responses import RedirectResponse #type: ignore
import modules.ResponseModels as ResponseModels
from slowapi import Limiter, _rate_limit_exceeded_handler #type: ignore
from slowapi.util import get_remote_address #type: ignore
from slowapi.errors import RateLimitExceeded #type: ignore
from fastapi_cache import FastAPICache #type: ignore
from fastapi_cache.backends.redis import RedisBackend #type: ignore
from fastapi_cache.decorator import cache #type: ignore

"""Get latest ReVanced releases from GitHub API."""

# Load config

config: dict = toml.load("config.toml")

# Redis connection parameters

redis_config: dict[ str, str | int ] = {
    "url": f"redis://{os.environ['REDIS_URL']}",
    "port": os.environ['REDIS_PORT'],
    "database": config['cache']['database'],
}

# Create releases instance

releases = Releases()

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

@app.get("/", response_class=RedirectResponse, status_code=301)
@limiter.limit(config['slowapi']['limit'])
async def root(request: Request, response: Response) -> RedirectResponse:
    """Brings up API documentation

    Returns:
        None: Redirects to /docs
    """
    return RedirectResponse(url="/docs")

@app.get('/tools', response_model=ResponseModels.ToolsResponseModel)
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def tools(request: Request, response: Response) -> dict:
    """Get patching tools' latest version.

    Returns:
        json: information about the patching tools' latest version
    """
    return await releases.get_latest_releases(config['app']['repositories'])

@app.get('/patches', response_model=ResponseModels.PatchesResponseModel)
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def patches(request: Request, response: Response) -> dict:
    """Get latest patches.

    Returns:
        json: list of latest patches
    """
    
    return await releases.get_patches_json()

@app.get('/contributors', response_model=ResponseModels.ContributorsResponseModel)
@limiter.limit(config['slowapi']['limit'])
@cache(config['cache']['expire'])
async def contributors(request: Request, response: Response) -> dict:
    """Get contributors.

    Returns:
        json: list of contributors
    """
    return await releases.get_contributors(config['app']['repositories'])

@app.on_event("startup")
async def startup() -> None:
    redis_url = f"{redis_config['url']}:{redis_config['port']}/{redis_config['database']}"
    redis =  aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    
    return None

# Run app
if __name__ == '__main__':
    uvicorn.run(app, host=config['uvicorn']['host'], port=config['uvicorn']['port'])