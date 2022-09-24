import os
import toml
from redis import asyncio as aioredis

# Load config

config: dict = toml.load("config.toml")

# Redis connection parameters

redis_config: dict[ str, str | int ] = {
    "url": f"redis://{os.environ['REDIS_URL']}",
    "port": os.environ['REDIS_PORT'],
}

class RedisConnector:
    """Implements the RedisConnector class for the ReVanced API"""
    
    def __init__(self, database: str) -> None:
        """Create Redis URL"""
        self.redis_url = f"{redis_config['url']}:{redis_config['port']}/{database}"
    
    def connect(self) -> aioredis.Redis:
        """Connect to Redis"""
        return aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)