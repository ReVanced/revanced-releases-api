
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from app.dependencies import load_config
from app.controllers.Releases import Releases
import app.models.ResponseModels as ResponseModels

router = APIRouter()

releases = Releases()

config: dict = load_config()

@router.get('/commits/{repository}/{current_version}/{target_tag}', response_model=ResponseModels.ChangelogsResponseModel, tags=['ReVanced Tools'])
@cache(config['cache']['expire'])
async def commits(repository: str, current_version: str, target_tag: str = "latest") -> str:
    """Get commit history from a given repository.

    Args:
        repository (str): Repository name
        current_version (str): current version(vx.x.x) installed
        target_tag (str): lateset(default), prerelease, recent, tag_name

    Returns:
        str: string containing the repository's commits between version
    """
    
    return await releases.get_commits(repository, current_version, target_tag)
