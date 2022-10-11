from fastapi import APIRouter, Request, Response
from fastapi_cache.decorator import cache
from app.dependencies import load_config
from app.controllers.Releases import Releases
import app.models.ResponseModels as ResponseModels

router = APIRouter()

releases = Releases()

config: dict = load_config()

@router.get('/changelogs/{org}/{repo}', response_model=ResponseModels.ChangelogsResponseModel, tags=['ReVanced Tools'])
@cache(config['cache']['expire'])
async def changelogs(request: Request, response: Response, org: str, repo: str, path: str) -> dict:
    """Get the latest changes from a repository.

    Returns:
        json: list of commits
    """
    return await releases.get_commits(
        org=org,
        repository=repo,
        path=path
        )
