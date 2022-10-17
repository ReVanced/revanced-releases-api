import time
import uuid
import secrets

class Generators:
    """Generates UUIDs and secrets"""
    
    async def generate_secret(self) -> str:
        """Generate a random secret

        Returns:
            str: A random secret
        """
        return secrets.token_urlsafe(32)

    async def generate_id(self) -> str:
        """Generate a random UUID

        Returns:
            str: A random UUID (str instead of UUID object)
        """
        return str(uuid.uuid4())
    
    async def generate_timestamp(self) -> int:
        """Generate a timestamp

        Returns:
            int: A timestamp
        """
        return int(time.time())
