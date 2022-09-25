import toml
from redis import asyncio as aioredis

import modules.utils.Logger as Logger
from modules.utils.Generators import Generators
from modules.models.AnnouncementModels import AnnouncementCreateModel, AnnouncementModel
from modules.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class Announcements:
    """Implements the announcements class for the ReVanced API"""
       
    redis = RedisConnector.connect(config['announcements']['database'])
    
    AnnouncementsLogger = Logger.AnnouncementsLogger()
    
    generators = Generators()
    
    async def store(self, announcement: AnnouncementCreateModel) -> str | bool:
        """Store an announcement in the database

        Args:
            announcement (AnnouncementCreateModel): Pydantic model of the announcement

        Returns:
            str | bool: UUID of the announcement or False if the announcement wasn't stored successfully
        """
        
        announcement_id: str = await self.generators.generate_id()
        
        timestamp = await self.generators.generate_timestamp()
        
        announcement_payload: dict[str, str | int] = {}
        
        announcement_payload['created_at'] = timestamp
        announcement_payload['updated_at'] = timestamp
        announcement_payload['owner'] = announcement.owner
        announcement_payload['title'] = announcement.title
        announcement_payload['content'] = announcement.content
        
        try:
            await self.redis.json().set(announcement_id, '$', announcement_payload)
            await self.AnnouncementsLogger.log("SET", None, announcement_id)
        except aioredis.RedisError as e:
            await self.AnnouncementsLogger.log("SET", e)
            return False
        
        return announcement_id
    
    async def exists(self, announcement_id: str) -> bool:
        """Check if an announcement exists in the database

        Args:
            announcement_id (str): UUID of the announcement

        Returns:
            bool: True if the announcement exists, False otherwise
        """
        try:
            if await self.redis.exists(announcement_id):
                await self.AnnouncementsLogger.log("EXISTS", None, announcement_id)
                return True
            else:
                await self.AnnouncementsLogger.log("EXISTS", None, announcement_id)
                return False
        except aioredis.RedisError as e:
            await self.AnnouncementsLogger.log("EXISTS", e)
            return False
    
    async def get(self, announcement_id: str) -> dict:
        """Get a announcement from the database

        Args:
            announcement_id (str): UUID of the announcement

        Returns:
            dict: Dict of the announcement or an empty dict if the announcement doesn't exist
        """
        
        if await self.exists(announcement_id):
            await self.AnnouncementsLogger.log("EXISTS", None, announcement_id)
            try:
                announcement: dict[str, str | int] = {}
                announcement["id"] = announcement_id
                
                announcement_payload: dict[str, str | int] = await self.redis.json().get(announcement_id)
                
                announcement |= announcement_payload
                
                await self.AnnouncementsLogger.log("GET", None, announcement_id)
            except aioredis.RedisError as e:
                await self.AnnouncementsLogger.log("GET", e)
                return {}
            return announcement
        else:
            return {}
        
    async def delete(self, announcement_id: str) -> bool:
        """Delete an announcement from the database

        Args:
            announcement_id (str): UUID of the announcement

        Returns:
            bool: True if the announcement was deleted successfully, False otherwise
        """
        
        if await self.exists(announcement_id):
            try:
                await self.redis.delete(announcement_id)
                await self.AnnouncementsLogger.log("DELETE", None, announcement_id)
            except aioredis.RedisError as e:
                await self.AnnouncementsLogger.log("DELETE", e)
                return False
            return True
        else:
            return False