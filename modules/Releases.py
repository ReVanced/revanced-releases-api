import os
import orjson
from base64 import b64decode
from modules.utils.HTTPXClient import HTTPXClient
from modules.utils.InternalCache import InternalCache


class Releases:
    
    """Implements the methods required to get the latest releases and patches from revanced repositories."""
 
    httpx_client = HTTPXClient.create()
    
    InternalCache = InternalCache()
    
    async def __get_release(self, repository: str) -> list:
        # Get assets from latest release in a given repository.
        #
        # Args:
        #    repository (str): Github's standard username/repository notation
        #
        # Returns:
        #    dict: dictionary of filename and download url
        
        assets: list = []
        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/releases/latest")
        
        if response.status_code == 200:
            release_assets: dict = response.json()['assets']
            release_version: str = response.json()['tag_name']
            release_tarball: str = response.json()['tarball_url']
            release_timestamp: str = response.json()['published_at']
            
            if release_assets:
                for asset in release_assets:
                    assets.append({ 'repository': repository,
                                    'version': release_version,
                                    'timestamp': asset['updated_at'],
                                    'name': asset['name'],
                                    'size': asset['size'],
                                    'browser_download_url': asset['browser_download_url'],
                                    'content_type': asset['content_type']
                                    })
            else:
                assets.append({ 'repository': repository,
                                'version': release_version,
                                'timestamp': release_timestamp,
                                'name': f"{repository.split('/')[1]}-{release_version}.tar.gz",
                                'browser_download_url': release_tarball,
                                'content_type': 'application/gzip'
                               })
        return assets

    async def get_latest_releases(self, repositories: list) -> dict:
        """Runs get_release() asynchronously for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing assets from each repository
        """
        
        releases: dict[str, list]
        
        if await self.InternalCache.exists('releases'):
            releases = await self.InternalCache.get('releases')
        else:
            releases = {}
            releases['tools'] = []
            
            for repository in repositories:
                files = await self.__get_release(repository)
                if files:
                    for file in files:
                        releases['tools'].append(file)
            await self.InternalCache.store('releases', releases)
        
        return releases
    
    async def __get_patches_json(self) -> dict:
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
        if await self.InternalCache.exists('patches'):
            patches = await self.InternalCache.get('patches')
        else:
            patches = await self.__get_patches_json()
            await self.InternalCache.store('patches', patches)
        
        return patches

    async def __get_contributors(self, repository: str) -> list:
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
        
        contributors: dict[str, list]
        
        if await self.InternalCache.exists('contributors'):
            contributors = await self.InternalCache.get('contributors')
        else:
            contributors = {}
            contributors['repositories'] = []
            for repository in repositories:
                if 'revanced' in repository:
                    repo_contributors = await self.__get_contributors(repository)
                    data = { 'name': repository, 'contributors': repo_contributors }
                    contributors['repositories'].append(data)
            await self.InternalCache.store('contributors', contributors)
        
        return contributors