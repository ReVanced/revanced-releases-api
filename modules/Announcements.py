import os
import toml
from typing import Optional
from redis import asyncio as aioredis

import modules.utils.Logger as Logger
from modules.models.ClientModels import ClientModel

class Announcements:
    """Implements the announcements class for the ReVanced API"""
    
    