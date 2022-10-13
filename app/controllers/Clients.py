from time import sleep
import toml
import orjson
from typing import Optional
import argon2
from redis import asyncio as aioredis
import aiofiles
import uvloop

import app.utils.Logger as Logger
from app.utils.Generators import Generators
from app.models.ClientModels import ClientModel
from app.utils.RedisConnector import RedisConnector

config: dict = toml.load("config.toml")

class Clients:
    
    """Implements a client for ReVanced Releases API."""
    
    uvloop.install()
    
    redis = RedisConnector.connect(config['clients']['database'])
    redis_tokens = RedisConnector.connect(config['tokens']['database'])
    
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
        
        client = ClientModel(id=client_id, secret=client_secret, admin=admin, active=True)
        
        return client
    
    async def store(self, client: ClientModel) -> bool:
        """Store a client in the database

        Args:
            client (ClientModel): Pydantic model of the client

        Returns:
            bool: True if the client was stored successfully, False otherwise
        """
        
        client_payload: dict[str, str | bool] = {}
        ph: argon2.PasswordHasher = argon2.PasswordHasher()
        
        client_payload['secret'] = ph.hash(client.secret)
        client_payload['admin'] = client.admin
        client_payload['active'] = client.active
        
        try:
            await self.redis.json().set(client.id, '$', client_payload)
            await self.UserLogger.log("SET", None, client.id)
        except aioredis.RedisError as e:
            await self.UserLogger.log("SET", e)
            raise e
        
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
            raise e
    
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
                client = ClientModel(id=client_id, secret=client_payload['secret'], admin=client_payload['admin'], active=True)
                await self.UserLogger.log("GET", None, client_id)
            except aioredis.RedisError as e:
                await self.UserLogger.log("GET", e)
                raise e
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
                raise e
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
        
        ph: argon2.PasswordHasher = argon2.PasswordHasher()
        
        updated: bool = False
        
        try:
            await self.redis.json().set(client_id, '.secret', ph.hash(new_secret))
            await self.UserLogger.log("UPDATE_SECRET", None, client_id)
            updated = True
        except aioredis.RedisError as e:
            await self.UserLogger.log("UPDATE_SECRET", e)
            raise e
        
        return updated
    
    async def authenticate(self, client_id: str, secret: str) -> bool:
        """Check if the secret of a client is correct

        Args:
            client_id (str): UUID of the client
            secret (str): Secret of the client

        Returns:
            bool: True if the secret is correct, False otherwise
        """
        
        ph: argon2.PasswordHasher = argon2.PasswordHasher()
        authenticated: bool = False
        client_secret: str = await self.redis.json().get(client_id, '.secret')
        
        try:
            if ph.verify(client_secret, secret):
                await self.UserLogger.log("CHECK_SECRET", None, client_id)
                
                if ph.check_needs_rehash(client_secret):
                    await self.redis.json().set(client_id, '.secret', ph.hash(secret))
                    await self.UserLogger.log("REHASH SECRET", None, client_id)
            authenticated = True
        except argon2.exceptions.VerifyMismatchError as e:
            await self.UserLogger.log("CHECK_SECRET", e)
            return authenticated

        return authenticated
    
    async def is_admin(self, client_id: str) -> bool:
        """Check if a client has admin access

        Args:
            client_id (str): UUID of the client

        Returns:
            bool: True if the client has admin access, False otherwise
        """
        
        client_admin: bool = False
        
        try:
            client_admin = await self.redis.json().get(client_id, '.admin')
            await self.UserLogger.log("CHECK_ADMIN", None, client_id)
        except aioredis.RedisError as e:
            await self.UserLogger.log("CHECK_ADMIN", e)
            raise e
        
        return client_admin
    
    
    async def is_active(self, client_id: str) -> bool:
        """Check if a client is active

        Args:
            client_id (str): UUID of the client

        Returns:
            bool: True if the client is active, False otherwise
        """
        
        client_active: bool = False
        
        try:
            client_active = await self.redis.json().get(client_id, '.active')
            await self.UserLogger.log("CHECK_ACTIVE", None, client_id)
        except aioredis.RedisError as e:
            await self.UserLogger.log("CHECK_ACTIVE", e)
            raise e
        
        return client_active
    
    async def status(self, client_id: str, active: bool) -> bool:
        """Activate a client
        
        Args:
            client_id (str): UUID of the client
            active (bool): True to activate the client, False to deactivate it
        
        Returns:
            bool: True if the client status was change successfully, False otherwise
        """
        
        changed: bool = False
        
        try:
            await self.redis.json().set(client_id, '.active', active)
            await self.UserLogger.log("ACTIVATE", None, client_id)
            changed = True
        except aioredis.RedisError as e:
            await self.UserLogger.log("ACTIVATE", e)
            raise e
        
        return changed
    
    async def ban_token(self, token: str) -> bool:
        """Ban a token

        Args:
            token (str): Token to ban

        Returns:
            bool: True if the token was banned successfully, False otherwise
        """
        
        banned: bool = False
        
        try:
            await self.redis_tokens.set(token, '')
            await self.UserLogger.log("BAN_TOKEN", None, token)
            banned = True
        except aioredis.RedisError as e:
            await self.UserLogger.log("BAN_TOKEN", e)
            raise e
        
        return banned
    
    async def is_token_banned(self, token: str) -> bool:
        """Check if a token is banned

        Args:
            token (str): Token to check

        Returns:
            bool: True if the token is banned, False otherwise
        """
        
        banned: bool = True
        
        try:
            banned = await self.redis_tokens.exists(token)
            await self.UserLogger.log("CHECK_TOKEN", None, token)
        except aioredis.RedisError as e:
            await self.UserLogger.log("CHECK_TOKEN", e)
            raise e
        
        return banned
    
    async def auth_checks(self, client_id: str, token: str) -> bool:
        """Check if a client exists, is active and the token isn't banned

        Args:
            client_id (str): UUID of the client
            secret (str): Secret of the client

        Returns:
            bool: True if the client exists, is active
            and the token isn't banned, False otherwise
        """

        if await self.exists(client_id):
            if await self.is_active(client_id):
                if not await self.is_token_banned(token):
                    return True
                else:
                    return False
            else:
                if not await self.is_token_banned(token):
                    await self.ban_token(token)
                    return False
        else:
            await self.ban_token(token)
            return False
        
        return False
    
    async def setup_admin(self) -> bool:
        """Create the admin user if it doesn't exist

        Returns:
            bool: True if the admin user was created successfully, False otherwise
        """
        created: bool = False
        
        if not await self.exists('admin'):
            admin_info: ClientModel = await self.generate()
            admin_info.id = 'admin'
            admin_info.admin = True
            try:
                await self.store(admin_info)
                await self.UserLogger.log("CREATE_ADMIN | ID |", None, admin_info.id)
                await self.UserLogger.log("CREATE_ADMIN | SECRET |", None, admin_info.secret)
                async with aiofiles.open("admin_info.json", "wb") as file:
                    await file.write(orjson.dumps(vars(admin_info)))
                    await self.UserLogger.log("CREATE_ADMIN | TO FILE", None, "admin_info.json")
                created = True
            except aioredis.RedisError as e:
                await self.UserLogger.log("CREATE_ADMIN", e)
                raise e
        
        return created