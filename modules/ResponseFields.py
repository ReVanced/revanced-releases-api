from enum import Enum

class LatestToolsFields(str, Enum):
    """Implements the fields for the /tools endpoint.

    Args:
        str (str): String
        Enum (Enum): Enum from pydantic
    """
    
    repository = 'repository'
    name = 'name'
    size = 'size'
    browser_download_url = 'browser_download_url'
    content_type = 'content_type'

class LatestPatchesFields(str, Enum):
    """Implements the fields for the /patches endpoint.

    Args:
        str (str): String
        Enum (Enum): Enum from pydantic
    """
    
    target_app = "target_app"
    patch_name = "patch_name"
    description = "description"
    target_version = "target_version"