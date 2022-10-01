import toml
from typing import Optional
from argon2 import PasswordHasher
from redis import asyncio as aioredis

import src.utils.Logger as Logger
from src.utils.Generators import Generators
from src.models.ClientModels import ClientModel
from src.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class Clients:
    
    """Implements a client for ReVanced Releases API."""
    
    redis = RedisConnector.connect(config['clients']['database'])
    
    UserLogger = Logger.UserLogger()
    
    generators = Generators()

    async def generate(self, admin: Optional[bool] = False) -> ClientModel:
        """Generate a new client

        Args:
            admin (Optional[bool], optional): Defines if the client should have admin access. Defaults to False.

        Returns:
            ClientModel: Pydantic model of the client
        """
        
        client_id: str = await self.generators.generate_id()
        client_secret: str = await self.generators.generate_secret()
        
        client = ClientModel(id=client_id, secret=client_secret, admin=admin)
        
        return client
    
    async def store(self, client: ClientModel) -> bool:
        """Store a client in the database

        Args:
            client (ClientModel): Pydantic model of the client

        Returns:
            bool: True if the client was stored successfully, False otherwise
        """
        
        client_payload: dict[str, str | bool] = {}
        ph = PasswordHasher()
        
        client_payload['secret'] = ph.hash(client.secret)
        client_payload['admin'] = client.admin
        
        try:
            await self.redis.json().set(client.id, '$', client_payload)
            await self.UserLogger.log("SET", None, client.id)
        except aioredis.RedisError as e:
            await self.UserLogger.log("SET", e)
            return False
        
        return True
    
    async def exists(self, client_id: str) -> bool:
        """Check if a client exists in the database

        Args:
            client_id (str): UUID of the client

        Returns:
            bool: True if the client exists, False otherwise
        """
        try:
            if await self.redis.exists(client_id):
                await self.UserLogger.log("EXISTS", None, client_id)
                return True
            else:
                await self.UserLogger.log("EXISTS", None, client_id)
                return False
        except aioredis.RedisError as e:
            await self.UserLogger.log("EXISTS", e)
            return False
    
    async def get(self, client_id: str) -> ClientModel | bool:
        """Get a client from the database

        Args:
            client_id (str): UUID of the client

        Returns:
            ClientModel | bool: Pydantic model of the client or False if the client doesn't exist
        """
        
        if await self.exists(client_id):
            try:
                client_payload: dict[str, str | bool] = await self.redis.json().get(client_id)
                client = ClientModel(id=client_id, secret=client_payload['secret'], admin=client_payload['admin'])
                await self.UserLogger.log("GET", None, client_id)
            except aioredis.RedisError as e:
                await self.UserLogger.log("GET", e)
                return False
            return client
        else:
            return False
        
    async def delete(self, client_id: str) -> bool:
        """Delete a client from the database

        Args:
            client_id (str): UUID of the client

        Returns:
            bool: True if the client was deleted successfully, False otherwise
        """
        
        if await self.exists(client_id):
            try:
                await self.redis.delete(client_id)
                await self.UserLogger.log("DELETE", None, client_id)
            except aioredis.RedisError as e:
                await self.UserLogger.log("DELETE", e)
                return False
            return True
        else:
            return False
        
    async def update_secret(self, client_id: str, new_secret: str) -> bool:
        """Update the secret of a client

        Args:
            client_id (str): UUID of the client
            new_secret (str): New secret of the client

        Returns:
            bool: True if the secret was updated successfully, False otherwise
        """
        try:
            ph = PasswordHasher()
            await self.redis.json().set(client_id, '.secret', ph.hash(new_secret))
            await self.UserLogger.log("UPDATE_SECRET", None, client_id)
        except aioredis.RedisError as e:
            await self.UserLogger.log("UPDATE_SECRET", e)
            return False
        return True