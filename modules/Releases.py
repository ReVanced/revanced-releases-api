import os
import pycmarkgfm
import httpx_cache
from typing import Dict, List
from base64 import b64decode
from bs4 import BeautifulSoup

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

    async def get_patches_readme(self, client: httpx_cache.AsyncClient) -> str:
        """Get revanced-patches repository's README.md.
        
        Returns:
            str: README.md content
        """
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
            content = await self.get_patches_readme(client)
            
        for line in content.splitlines():
            if line.startswith(u'###'):
                packages['apps'].append(line.split('`')[1])
        
        return packages

    async def get_latest_patches(self) -> dict:
        """Get latest patches from revanced-patches repository.
        
        Returns:
            dict: Patches available for a given app
        """
        patches: Dict[str, List] = {}
        patches['patches'] = []
        
        async with httpx_cache.AsyncClient(headers=self.headers, http2=True) as client:
            content = await self.get_patches_readme(client)
        
        html = pycmarkgfm.gfm_to_html(content)
        soup = BeautifulSoup(html, 'lxml')
        
        headings = soup.find_all('h3')
        
        for heading in headings:
            app_name = heading.text.split(' ')[1]
            for patch in heading.find_next_sibling().find_all('tr')[1:]:
                app_patches = patch.find_all('td')
                patches['patches'].append({"target_app": app_name,
                                           "patch_name" : app_patches[0].text,
                                           "description": app_patches[1].text,
                                           "target_version": app_patches[2].text
                                           })
            
        return patches
