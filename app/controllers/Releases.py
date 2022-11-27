import asyncio
import uvloop
import orjson
from base64 import b64decode
from toolz.dicttoolz import keyfilter
from app.utils.HTTPXClient import HTTPXClient

class Releases:

    """Implements the methods required to get the latest releases and patches from revanced repositories."""

    uvloop.install()

    httpx_client = HTTPXClient.create()

    async def __get_release(self, repository: str) -> list:
        """Get assets from latest release in a given repository.

        Args:
           repository (str): Github's standard username/repository notation

        Returns:
           dict: dictionary of filename and download url
        """

        assets: list = []
        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/releases/latest")

        if response.status_code == 200:
            release_assets: dict = response.json()['assets']
            release_version: str = response.json()['tag_name']
            release_tarball: str = response.json()['tarball_url']
            release_timestamp: str = response.json()['published_at']

            def get_asset_data(asset: dict) -> dict:
                return {'repository': repository,
                        'version': release_version,
                        'timestamp': asset['updated_at'],
                        'name': asset['name'],
                        'size': asset['size'],
                        'browser_download_url': asset['browser_download_url'],
                        'content_type': asset['content_type']
                        }

            no_release_assets_data: dict = {'repository': repository,
                                            'version': release_version,
                                            'timestamp': release_timestamp,
                                            'name': f"{repository.split('/')[1]}-{release_version}.tar.gz",
                                            'browser_download_url': release_tarball,
                                            'content_type': 'application/gzip'
                                            }
            if release_assets:
                assets = [get_asset_data(asset) for asset in release_assets]
            else:
                assets.append(no_release_assets_data)

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

        results: list = await asyncio.gather(*[self.__get_release(repository) for repository in repositories])

        releases['tools'] = [asset for result in results for asset in result]

        return releases

    async def __get_patches_json(self) -> dict:
        """Get revanced-patches repository's README.md.

        Returns:
           dict: JSON content
        """

        response = await self.httpx_client.get(f"https://api.github.com/repos/revanced/revanced-patches/contents/patches.json")
        content = orjson.loads(
            b64decode(response.json()['content']).decode('utf-8'))

        return content

    async def get_patches_json(self) -> dict:
        """Get patches.json from revanced-patches repository.

        Returns:
            dict: Patches available for a given app
        """

        patches: dict = await self.__get_patches_json()

        return patches

    async def __get_contributors(self, repository: str) -> list:
        """Get contributors from a given repository.

        Args:
           repository (str): Github's standard username/repository notation

        Returns:
           list: a list of dictionaries containing the repository's contributors
        """

        keep: set = {'login', 'avatar_url', 'html_url'}

        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/contributors")

        # Looping over each contributor, filtering each contributor so that
        # keyfilter() returns a dictionary with only the key-value pairs that are in the "keep" set.
        contributors: list = [keyfilter(lambda k: k in keep, contributor) for contributor in response.json()]

        return contributors

    async def get_contributors(self, repositories: list) -> dict:
        """Runs get_contributors() asynchronously for each repository.

        Args:
            repositories (list): List of repositories in Github's standard username/repository notation

        Returns:
            dict: A dictionary containing the contributors from each repository
        """

        contributors: dict[str, list]

        contributors = {}
        contributors['repositories'] = []

        revanced_repositories = [
            repository for repository in repositories if 'revanced' in repository]

        results: list[dict] = await asyncio.gather(*[self.__get_contributors(repository) for repository in revanced_repositories])

        for key, value in zip(revanced_repositories, results):
            data = {'name': key, 'contributors': value}
            contributors['repositories'].append(data)

        return contributors

    async def get_commits(self, org: str, repository: str, path: str) -> dict:
        """Get commit history from a given repository.

        Args:
            org (str): Username of the organization | valid values: revanced or vancedapp
            repository (str): Repository name
            path (str): Path to the file
            per_page (int): Number of commits to return
            since (str): ISO 8601 timestamp

        Raises:
            Exception: Raise a generic exception if the organization is not revanced or vancedapp

        Returns:
            dict: a dictionary containing the repository's latest commits
        """

        payload: dict = {}
        payload["repository"] = f"{org}/{repository}"
        payload["path"] = path
        payload["commits"] = []

        if org == 'revanced' or org == 'vancedapp':
            _releases = await self.httpx_client.get(
                f"https://api.github.com/repos/{org}/{repository}/releases?per_page=2"
            )

            releases = _releases.json()

            since = releases[1]['created_at']
            until = releases[0]['created_at']

            _response = await self.httpx_client.get(
                f"https://api.github.com/repos/{org}/{repository}/commits?path={path}&since={since}&until={until}"
            )

            response = _response.json()

            for commit in response:
                data: dict[str, str] = {}
                data["sha"] = commit["sha"]
                data["author"] = commit["commit"]["author"]["name"]
                data["message"] = commit["commit"]["message"]
                data["html_url"] = commit["html_url"]
                payload['commits'].append(data)

            return payload
        else:
            raise Exception("Invalid organization.")
