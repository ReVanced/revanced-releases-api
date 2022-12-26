from fastapi_cache.decorator import cache
from fastapi import APIRouter, Request, Response

import app.models.ResponseModels as ResponseModels
from app.controllers.Socials import Socials

from app.dependencies import load_config

router = APIRouter()

socials = Socials()

config: dict = load_config()

@router.get('/socials', response_model=ResponseModels.SocialsResponseModel, tags=['ReVanced Socials'])
@cache(config['cache']['expire'])
async def get_socials(request: Request, response: Response) -> dict:
    """Get ReVanced social links.

    Returns:
        json: dictionary of ReVanced social links
    """

    return await socials.get_socials()
