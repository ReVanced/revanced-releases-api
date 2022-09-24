import os
import toml
from typing import Any
from redis import asyncio as aioredis

import modules.utils.Logger as Logger
from modules.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class InternalCache:
    """Implements an internal cache for ReVanced Releases API."""
    
    redis_connector = RedisConnector(config['internal-cache']['database'])
    
    redis = redis_connector.connect()
    
    InternalCacheLogger = Logger.InternalCacheLogger()
        
    async def store(self, key: str, value: dict) -> None:
        """Stores a key-value pair in the cache.

        Args:
            key (str): the key to store
            value (dict): the JSON value to store
        """
        try:
            await self.redis.json().set(key, '$', value)
            await self.redis.expire(key, config['internal-cache']['expire'])
            await self.InternalCacheLogger.log("SET", None, key)
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("SET", e)
        
    async def delete(self, key: str) -> None:
        """Removes a key-value pair from the cache.

        Args:
            key (str): the key to delete
        """
        try:
            await self.redis.delete(key)
            await self.InternalCacheLogger.log("DEL", None, key)
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("DEL", e)
        
    async def get(self, key: str) -> dict:
        """Gets a key-value pair from the cache.

        Args:
            key (str): the key to retrieve

        Returns:
            dict: the JSON value stored in the cache or an empty dict if key doesn't exist or an error occurred
        """
        try:
            payload: dict[Any, Any] = await self.redis.json().get(key)
            await self.InternalCacheLogger.log("GET", None, key)
            return payload
        except aioredis.RedisError as e:
            await self.InternalCacheLogger.log("GET", e)
            return {}
    
    async def exists(self, key: str) -> bool:
        """Checks if a key exists in the cache.

        Args:
            key (str): key to check

        Returns:
            bool: True if key exists, False if key doesn't exist or an error occurred
        """
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

    
    