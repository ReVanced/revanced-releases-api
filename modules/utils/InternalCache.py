import os
import toml
import orjson
import msgpack
import aioredis

import modules.utils.Logger as Logger

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
    
    InternalCacheLogger = Logger.InternalCacheLogger()
        
    async def store(self, key: str, value: dict) -> None:
        try:
            await self.redis.set(key, orjson.dumps(value), ex=config['internal-cache']['expire'])
            await self.InternalCacheLogger.log("SET", None, key)
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("SET", e)
        
    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
            await self.InternalCacheLogger.log("DEL", None, key)
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("DEL", e)
        
    async def update(self, key: str, value: dict) -> None:
        try:
            await self.redis.set(key, orjson.dumps(value), ex=config['internal-cache']['expire'])
            await self.InternalCacheLogger.log("SET", None, key)
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("SET", e)
        
    async def get(self, key: str) -> dict:
        try:
            payload = orjson.loads(await self.redis.get(key))
            await self.InternalCacheLogger.log("GET", None, key)
            return payload
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("GET", e)
            return {}
    
    async def exists(self, key: str) -> bool:
        try:
            if await self.redis.exists(key):
                await self.InternalCacheLogger.log("EXISTS", None, key)
                return True
            else:
                await self.InternalCacheLogger.log("EXISTS", None, key)
                return False
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("EXISTS", e)
            return False

    
    