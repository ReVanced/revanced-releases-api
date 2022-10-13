import toml
from redis import asyncio as aioredis
import app.utils.Logger as Logger
from app.models.MirrorModels import MirrorModel, MirrorStoreModel
from app.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class Mirrors:
    """Implements the Mirror class for the ReVanced API"""
    
    redis = RedisConnector.connect(config['mirrors']['database'])
    
    MirrorsLogger = Logger.MirrorsLogger()
    
    async def assemble_key(self, org: str, repo: str, version: str) -> str:
        """Assemble the Redis key for the cdn
        
        Returns:
            str: The Redis key
        """
        
        return f"{org}/{repo}/{version}"
    
    async def store(self, org: str, repo: str, version: str, mirror: MirrorStoreModel) -> bool:
        """Store mirrors in the database

        Args:
            mirror (MirrorStoreModel): Pydantic model of the mirror information

        Returns:
            bool: True if data was stored successfully, False otherwise
        """
        
        key = await self.assemble_key(org, repo, version)
        mirror_payload: dict[str, str | list[str]] = {}
        
        mirror_payload['cid'] = mirror.cid
        mirror_payload['filenames'] = mirror.filenames
        
        try:
            await self.redis.json().set(key, '$', mirror_payload)
            await self.MirrorsLogger.log("SET", None, key)
        except aioredis.RedisError as e:
            await self.MirrorsLogger.log("SET", e)
            raise e
        
        return True
    
    async def exists(self, org: str, repo: str, version: str) -> bool:
        """Check if a cdn exists in the database

        Returns:
            bool: True if the cdn exists, False otherwise
        """
        
        key = await self.assemble_key(org, repo, version)
        
        try:
            if await self.redis.exists(key):
                await self.MirrorsLogger.log("EXISTS", None, key)
                return True
            else:
                return False
        except aioredis.RedisError as e:
            await self.MirrorsLogger.log("EXISTS", e)
            raise e

    async def get(self, org: str, repo: str, version: str) -> MirrorModel:
        """Get the mirror information from the database

        Returns:
            dict[str, str | int]: The mirror information
        """
        
        key = await self.assemble_key(org, repo, version)
        
        try:
            payload: dict[str, str | list[str]] = await self.redis.json().get(key)
            
            mirror = MirrorModel(
                repository=f"{org}/{repo}",
                version=version,
                cid=payload['cid'],
                filenames=payload['filenames']
            )
            
            await self.MirrorsLogger.log("GET", None, key)
            return mirror
        except aioredis.RedisError as e:
            await self.MirrorsLogger.log("GET", e)
            raise e

    async def delete(self, org: str, repo: str, version: str) -> bool:
        """Delete the cdn from the database

        Returns:
            bool: True if the cdn was deleted successfully, False otherwise
        """
        
        key = await self.assemble_key(org, repo, version)
        
        try:
            await self.redis.delete(key)
            await self.MirrorsLogger.log("DELETE", None, key)
            return True
        except aioredis.RedisError as e:
            await self.MirrorsLogger.log("DELETE", e)
            raise e
        
        