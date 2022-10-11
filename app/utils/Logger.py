import sys
import logging
from loguru import logger
from redis import RedisError
from argon2.exceptions import VerifyMismatchError

class HTTPXLogger():
    """Logger adapter for HTTPX."""
    
    async def log_request(self, request) -> None:
        """Logs HTTPX requests
        
        Returns:
            None
        """
        
        logger.info(f"[HTTPX] Request: {request.method} {request.url} - Waiting for response")
        
    async def log_response(self, response) -> None:
        """Logs HTTPX responses
        
        Returns:
            None
        """
        request = response.request
        
        logger.info(f"[HTTPX] Response: {request.method} {request.url} - Status: {response.status_code} {response.reason_phrase}")

class InternalCacheLogger:
    async def log(self, operation: str, result: RedisError | None = None, key: str = "",) -> None:
        """Logs internal cache operations
        
        Args:
            operation (str): Operation name
            key (str): Key used in the operation
        """
        if type(result) is RedisError:
            logger.error(f"[InternalCache] REDIS {operation} - Failed with error: {result}")
        else:
            logger.info(f"[InternalCache] REDIS {operation} {key} - OK")

class UserLogger:
    async def log(self, operation: str, result: RedisError | VerifyMismatchError | None = None,
                  key: str = "",) -> None:
        """Logs internal cache operations
        
        Args:
            operation (str): Operation name
            key (str): Key used in the operation
        """
        if type(result) is RedisError:
            logger.error(f"[User] REDIS {operation} - Failed with error: {result}")
        else:
            logger.info(f"[User] REDIS {operation} {key} - OK")

class AnnouncementsLogger:
    async def log(self, operation: str, result: RedisError | None = None, key: str = "") -> None:
        """Logs internal cache operations
        
        Args:
            operation (str): Operation name
            key (str): Key used in the operation
        """
        if type(result) is RedisError:
            logger.error(f"[User] REDIS {operation} - Failed with error: {result}")
        else:
            logger.info(f"[User] REDIS {operation} {key} - OK")

def setup_logging(LOG_LEVEL: str, JSON_LOGS: bool) -> None:
    
    """Setup logging for uvicorn and FastAPI."""
    
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
