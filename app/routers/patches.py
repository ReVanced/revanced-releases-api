from fastapi import APIRouter, Request, Response
from fastapi_cache.decorator import cache
from app.dependencies import load_config
from app.controllers.Releases import Releases
import app.models.ResponseModels as ResponseModels

router = APIRouter()

releases = Releases()

config: dict = load_config()

@router.get('/patches/{tag}', response_model=ResponseModels.PatchesResponseModel, tags=['ReVanced Tools'])
@cache(config['cache']['expire'])
async def patches(request: Request, response: Response,
                  tag: str = config['repositories']['patches'][1]) -> dict:
    """Get latest patches.

    Returns:
        json: list of latest patches
    """
    
    return await releases.get_patches_json(config['repositories']['patches'][0], tag)
