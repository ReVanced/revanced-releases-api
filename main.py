#!/usr/bin/env python3

import toml
import uvicorn
from fastapi import FastAPI, Request, Response
from modules.Releases import Releases
from fastapi.responses import RedirectResponse
import modules.ResponseModels as ResponseModels
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

"""Get latest ReVanced releases from GitHub API."""

# Load config

config = toml.load("config.toml")

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

# Routes

@app.get("/", response_class=RedirectResponse, status_code=301)
@limiter.limit(config['slowapi']['limit'])
async def root(request: Request, response: Response) -> RedirectResponse:
    """Brings up API documentation

    Returns:
        None: Redirects to /docs
    """
    return RedirectResponse(url="/docs")

@app.get('/tools', response_model=ResponseModels.LatestTools)
@limiter.limit(config['slowapi']['limit'])
async def tools(request: Request, response: Response) -> dict:
    """Get patching tools' latest version.

    Returns:
        json: information about the patching tools' latest version
    """
    return await releases.get_latest_releases(config['app']['repositories'])

@app.get('/apps', response_model=ResponseModels.SupportedApps)
@limiter.limit(config['slowapi']['limit'])
async def apps(request: Request, response: Response) -> dict:
    """Get patchable apps.

    Returns:
        json: list of supported apps
    """
    return await releases.get_patchable_apps()

@app.get('/patches', response_model=ResponseModels.Patches)
@limiter.limit(config['slowapi']['limit'])
async def patches(request: Request, response: Response) -> dict:
    """Get latest patches.

    Returns:
        json: list of latest patches
    """
    
    return await releases.get_patches_json()

# Run app
if __name__ == '__main__':
    uvicorn.run(app, host=config['uvicorn']['host'], port=config['uvicorn']['port'])