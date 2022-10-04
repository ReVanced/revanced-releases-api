import toml
from redis import asyncio as aioredis

import src.utils.Logger as Logger
from src.utils.Generators import Generators
from src.models.AnnouncementModels import AnnouncementCreateModel
from src.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class Announcements:
    """Implements the announcements class for the ReVanced API"""
       
    redis = RedisConnector.connect(config['announcements']['database'])
    
    AnnouncementsLogger = Logger.AnnouncementsLogger()
    
    generators = Generators()
    
    async def store(self, announcement: AnnouncementCreateModel) -> bool:
        """Store an announcement in the database

        Args:
            announcement (AnnouncementCreateModel): Pydantic model of the announcement

        Returns:
            str | bool: UUID of the announcement or False if the announcement wasn't stored successfully
        """
        
        announcement_id: str = "announcement"
        
        timestamp = await self.generators.generate_timestamp()
        
        announcement_payload: dict[str, str | int] = {}
        
        announcement_payload['created_at'] = timestamp
        announcement_payload['author'] = announcement.author
        announcement_payload['type'] = announcement.type
        announcement_payload['title'] = announcement.title
        announcement_payload['content'] = announcement.content
        
        try:
            await self.redis.json().set(announcement_id, '$', announcement_payload)
            await self.AnnouncementsLogger.log("SET", None, announcement_id)
        except aioredis.RedisError as e:
            await self.AnnouncementsLogger.log("SET", e)
            raise e
        
        return True
    
    async def exists(self) -> bool:
        """Check if an announcement exists in the database

        Returns:
            bool: True if the announcement exists, False otherwise
        """
        try:
            if await self.redis.exists("announcement"):
                await self.AnnouncementsLogger.log("EXISTS", None, "announcement")
                return True
            else:
                await self.AnnouncementsLogger.log("EXISTS", None, "announcement")
                return False
        except aioredis.RedisError as e:
            await self.AnnouncementsLogger.log("EXISTS", e)
            raise e
    
    async def get(self) -> dict:
        """Get a announcement from the database

        Returns:
            dict: Dict of the announcement or an empty dict if the announcement doesn't exist
        """
        
        if await self.exists():
            try:
                announcement: dict[str, str | int] = await self.redis.json().get("announcement")
                await self.AnnouncementsLogger.log("GET", None, "announcement")
            except aioredis.RedisError as e:
                await self.AnnouncementsLogger.log("GET", e)
                return {}
            return announcement
        else:
            return {}
        
    async def delete(self) -> bool:
        """Delete an announcement from the database

        Returns:
            bool: True if the announcement was deleted successfully, False otherwise
        """
        
        if await self.exists():
            try:
                await self.redis.delete("announcement")
                await self.AnnouncementsLogger.log("DELETE", None, "announcement")
            except aioredis.RedisError as e:
                await self.AnnouncementsLogger.log("DELETE", e)
                return False
            return True
        else:
            return False