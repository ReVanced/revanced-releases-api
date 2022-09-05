import os
import orjson #type: ignore
import httpx_cache #type: ignore
from base64 import b64decode
from modules.InternalCache import InternalCache

class Releases:
    
    """Implements the methods required to get the latest releases and patches from revanced repositories."""

    headers = {'Accept': "application/vnd.github+json",
               'Authorization': "token " + os.environ['GITHUB_TOKEN']
               }
    
    httpx_client = httpx_cache.AsyncClient(headers=headers, http2=True)
    InternalCache = InternalCache()
    
    async def _get_release(self, repository: str) -> list:
        # Get assets from latest release in a given repository.
        #
        # Args:
        #    repository (str): Github's standard username/repository notation
        #
        # Returns:
        #    dict: dictionary of filename and download url
        
        assets = []
        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/releases/latest")
        
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
        
        releases: dict[str, list] = {}
        releases['tools'] = []
        
        try:
            cached_releases = await self.InternalCache.get("releases")
            return cached_releases
        except:
            for repository in repositories:
                files = await self._get_release(repository)
                if files:
                    for file in files:
                        releases['tools'].append(file)
            await self.InternalCache.store('releases', releases)
        
        return releases
    
    async def _get_patches_json(self) -> dict:
        # Get revanced-patches repository's README.md.
        #
        # Returns:
        #    dict: JSON content
        #
        
        response = await self.httpx_client.get(f"https://api.github.com/repos/revanced/revanced-patches/contents/patches.json")
        content = orjson.loads(b64decode(response.json()['content']).decode('utf-8'))
        
        return content
    
    async def get_patches_json(self) -> dict:
        """Get patches.json from revanced-patches repository.
        
        Returns:
            dict: Patches available for a given app
        """
        try:
            cached_patches = await self.InternalCache.get("patches")
            return cached_patches
        except:
            patches = await self._get_patches_json()
            await self.InternalCache.store('patches', patches)
        
        return patches

    async def _get_contributors(self, repository: str) -> list:
        # Get contributors from a given repository.
        #
        # Args:
        #    repository (str): Github's standard username/repository notation
        #
        # Returns:
        #    list: a list of dictionaries containing the repository's contributors
        
        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/contributors")
        
        return response.json()
    
    async def get_contributors(self, repositories: list) -> dict:
        """Runs get_contributors() asynchronously for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing the contributors from each repository
        """
        
        contributors: dict[str, list] = {}
        contributors['repositories'] = []
        
        try:
            cached_contributors = await self.InternalCache.get("contributors")
            return cached_contributors
        except:
            for repository in repositories:
                if 'revanced' in repository:
                    repo_contributors = await self._get_contributors(repository)
                    data = { 'name': repository, 'contributors': repo_contributors }
                    contributors['repositories'].append(data)
            await self.InternalCache.store('contributors', contributors)
        
        return contributors