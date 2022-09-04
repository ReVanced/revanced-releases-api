import os
import toml
import msgpack
import aioredis

# Load config

config: dict = toml.load("config.toml")

# Redis connection parameters

redis_config: dict[ str, str | int ] = {
    "url": f"redis://{os.environ['REDIS_URL']}",
    "port": os.environ['REDIS_PORT'],
    "database": config['internal-cache']['database'],
}

class InternalCache:
    """Implements an internal cache for ReVanced Releases API."""
    
    redis_url = f"{redis_config['url']}:{redis_config['port']}/{redis_config['database']}"
    redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
    async def store(self, key: str, value: dict) -> None:
        await self.redis.set(key, msgpack.packb(value), ex=config['internal-cache']['expire'])
        
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
        
    async def update(self, key: str, value: dict) -> None:
        await self.redis.set(key, msgpack.packb(value), ex=config['internal-cache']['expire'])
        
    async def get(self, key: str) -> dict:
        return msgpack.unpackb(await self.redis.get(key))
        

    
    