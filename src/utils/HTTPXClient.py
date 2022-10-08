import os
import httpx_cache
import src.utils.Logger as Logger

class HTTPXClient:
    
    """Implements the methods required to get the latest releases and patches from revanced repositories."""
    
    @staticmethod
    def create() -> httpx_cache.AsyncClient:
        """Create HTTPX client with cache

        Returns:
            httpx_cache.AsyncClient: HTTPX client with cache
        """
    
        headers = {'Accept': "application/vnd.github+json",
                'Authorization': "token " + os.environ['GITHUB_TOKEN']
                }
        
        httpx_logger = Logger.HTTPXLogger()
        
        httpx_client = httpx_cache.AsyncClient(
            headers=headers,
            http2=True,
            event_hooks={
                'request': [httpx_logger.log_request],
                'response': [httpx_logger.log_response]
                }
            )
        
        return httpx_client