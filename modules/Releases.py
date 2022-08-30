import os
import orjson
import httpx_cache
from typing import Dict, List
from base64 import b64decode

class Releases:
    
    """Implements the methods required to get the latest releases and patches from revanced repositories."""

    headers = {'Accept': "application/vnd.github+json",
               'Authorization': "token " + os.environ['GITHUB_TOKEN']
               }
    
    async def get_release(self, client: httpx_cache.AsyncClient, repository: str) -> list:
        """Get assets from latest release in a given repository.

        Args:
            client (httpx_cache.AsyncClient): httpx_cache reusable async client
            repository (str): Github's standard username/repository notation

        Returns:
            dict: dictionary of filename and download url
        """
        assets = []
        response = await client.get(f"https://api.github.com/repos/{repository}/releases/latest")
        
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
        """Runs get_release() in parallel for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing assets from each repository
        """
        releases: Dict[str, List] = {}
        releases['tools'] = []
        
        async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
            for repository in repositories:
                files = await self.get_release(client, repository)
                for file in files:
                    releases['tools'].append(file)
        
        return releases

    async def _get_patches_readme(self, client: httpx_cache.AsyncClient) -> str:
        # Get revanced-patches repository's README.md.
        #
        # Returns:
        #    str: README.md content
        #
        
        response = await client.get(f"https://api.github.com/repos/revanced/revanced-patches/contents/README.md")
        
        return b64decode(response.json()['content']).decode('utf-8')

    async def get_patchable_apps(self) -> dict:
        """Get patchable apps from revanced-patches repository.
        
        Returns:
            dict: Apps available for patching
        """
        packages: Dict[str, List] = {}
        packages['apps'] = []
        
        async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
            content = await self._get_patches_readme(client)
            
        for line in content.splitlines():
            if line.startswith(u'###'):
                packages['apps'].append(line.split('`')[1])
        
        return packages
    
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
        async def generate_simplified_json(payload: dict) -> dict:
            return {}    
        
        async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
            content = await self._get_patches_json(client)
        
        if simplified:
            return await generate_simplified_json(content)
        
        return content
