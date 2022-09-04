import os
import orjson
import httpx_cache
from typing import Dict, List
from base64 import b64decode
from modules.InternalCache import InternalCache

class Releases:
    
    InternalCache = InternalCache()
    
    """Implements the methods required to get the latest releases and patches from revanced repositories."""

    headers = {'Accept': "application/vnd.github+json",
               'Authorization': "token " + os.environ['GITHUB_TOKEN']
               }
    
    async def _get_release(self, client: httpx_cache.AsyncClient, repository: str) -> list:
        # Get assets from latest release in a given repository.
        #
        # Args:
        #    client (httpx_cache.AsyncClient): httpx_cache reusable async client
        #    repository (str): Github's standard username/repository notation
        #
        # Returns:
        #    dict: dictionary of filename and download url
        
        assets = []
        response = await client.get(f"https://api.github.com/repos/{repository}/releases/latest")
        
        if response.status_code == 200:
            release_assets = response.json()['assets']
    
            for asset in release_assets:
                assets.append({ 'repository': repository,
                                'name': asset['name'],
                                'size': asset['size'],
                                'browser_download_url': asset['browser_download_url'],
                                'content_type': asset['content_type']
                                })
            
        return assets

    async def get_latest_releases(self, repositories: list) -> dict:
        """Runs get_release() asynchronously for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing assets from each repository
        """
        
        releases: Dict[str, List] = {}
        releases['tools'] = []
        
        try:
            cached_releases = await self.InternalCache.get("releases")
            return cached_releases
        except:
            async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
                for repository in repositories:
                    files = await self._get_release(client, repository)
                    if files:
                        for file in files:
                            releases['tools'].append(file)
            await self.InternalCache.store('releases', releases)
        
        return releases
    
    async def _get_patches_json(self, client: httpx_cache.AsyncClient) -> dict:
        # Get revanced-patches repository's README.md.
        #
        # Returns:
        #    dict: JSON content
        #
        
        content = await client.get(f"https://api.github.com/repos/revanced/revanced-patches/contents/patches.json")
        
        return orjson.loads(b64decode(content.json()['content']).decode('utf-8'))
    
    async def get_patches_json(self, simplified: bool = False) -> dict:
        """Get patches.json from revanced-patches repository.
        
        Args:
            simplified (bool): If True, returns a simplified version of patches.json
        
        Returns:
            dict: Patches available for a given app
        """
        try:
            cached_patches = await self.InternalCache.get("patches")
            return cached_patches
        except:
            async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
                patches = await self._get_patches_json(client)
                await self.InternalCache.store('patches', patches)
        
        return patches

    async def _get_contributors(self, client: httpx_cache.AsyncClient, repository: str) -> list:
        # Get contributors from a given repository.
        #
        # Args:
        #    client (httpx_cache.AsyncClient): httpx_cache reusable async client
        #    repository (str): Github's standard username/repository notation
        #
        # Returns:
        #    list: a list of dictionaries containing the repository's contributors
        
        response = await client.get(f"https://api.github.com/repos/{repository}/contributors")
        
        return response.json()
    
    async def get_contributors(self, repositories: list) -> dict:
        """Runs get_contributors() asynchronously for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing the contributors from each repository
        """
        
        contributors: Dict[str, List] = {}
        contributors['repositories'] = []
        
        try:
            cached_contributors = await self.InternalCache.get("contributors")
            return cached_contributors
        except:
            async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
                for repository in repositories:
                    if 'revanced' in repository:
                        repo_contributors = await self._get_contributors(client, repository)
                        data = { 'name': repository, 'contributors': repo_contributors }
                        contributors['repositories'].append(data)
            await self.InternalCache.store('contributors', contributors)
        
        return contributors