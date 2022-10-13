from fastapi import APIRouter, Request, Response
from fastapi_cache.decorator import cache
from app.dependencies import load_config
from app.controllers.Releases import Releases
import app.models.ResponseModels as ResponseModels

router = APIRouter()

releases = Releases()

config: dict = load_config()

@router.get('/contributors', response_model=ResponseModels.ContributorsResponseModel, tags=['ReVanced Tools'])
@cache(config['cache']['expire'])
async def contributors(request: Request, response: Response) -> dict:
    """Get contributors.

    Returns:
        json: list of contributors
    """
    return await releases.get_contributors(config['app']['repositories'])