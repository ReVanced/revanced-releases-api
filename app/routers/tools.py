from fastapi import APIRouter, Request, Response
from fastapi_cache.decorator import cache
from app.dependencies import load_config
from app.controllers.Releases import Releases
import app.models.ResponseModels as ResponseModels

router = APIRouter()

releases = Releases()

config: dict = load_config()
repos= dict(config['repositories'].values())

@router.get('/tools/{repositories}', response_model=ResponseModels.ToolsResponseModel, tags=['ReVanced Tools'])
@cache(config['cache']['expire'])
async def tools(request: Request, response: Response,
                repositories: dict = repos) -> dict:
    """Get patching tools' latest version.

    Returns:
        json: information about the patching tools' latest version
    """
    return await releases.get_latest_releases(repositories)
