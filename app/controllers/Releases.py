import asyncio
import uvloop
from toolz.dicttoolz import keyfilter
import asyncstdlib.builtins as a
from app.utils.HTTPXClient import HTTPXClient

class Releases:

    """Implements the methods required to get the latest releases and patches from revanced repositories."""

    uvloop.install()

    httpx_client = HTTPXClient.create()

    async def get_tag_release(self, repository: str, tag: str) -> dict:
        """get tag name from github release api.
            
            arg:
                repository (str): Github's standard username/repository notation
                tag (str): lateset- to get latest release
                           prerelease - to get lateset prerelease
                           recent - to get recent release either prerelease or stable whichever is recent
                           tag_name - supply a valid version tag

            returns:
                dict: Release dict of supplied tag arg.
        """

        response = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/releases")
        release_dict = None

        if response.status_code == 200:
            for release in response.json():
                match tag:
                    case "recent":
                        release_dict = release
                        break

                    case "prerelease":
                        if release['prerelease']:
                            release_dict = release
                            break

                    case "latest":
                        if not release['prerelease']:
                            release_dict = release
                            break

                    case _:
                        if tag == release['tag_name']:
                            release_dict = release
                            break

        return release_dict

    async def __get_release(self, repository: str, tag: str = "latest") -> list:
        """Get assets from latest release in a given repository.

        Args:
            repository (str): Github's standard username/repository notation
            tag (str): lateset(default)/ prerelease/ recent/ tag_name
                        see get_tag_release() for more details.

        Returns:
           dict: dictionary of filename and download url
        """

        assets: list = []
        release_dict = await self.get_tag_release(repository, tag)

        release_assets: dict = release_dict['assets']
        release_version: str = release_dict['tag_name']
        release_tarball: str = release_dict['tarball_url']
        release_timestamp: str = release_dict['published_at']

        async def get_asset_data(asset: dict) -> dict:
            return {'repository': repository,
                    'version': release_version,
                    'timestamp': asset['updated_at'],
                    'name': asset['name'],
                    'size': asset['size'],
                    'browser_download_url': asset['browser_download_url'],
                    'content_type': asset['content_type']
                    }

        if release_assets:
            assets = await asyncio.gather(*[get_asset_data(asset) for asset in release_assets])
        else:
            no_release_assets_data: dict = {'repository': repository,
                                'version': release_version,
                                'timestamp': release_timestamp,
                                'name': f"{repository.split('/')[1]}-{release_version}.tar.gz",
                                'browser_download_url': release_tarball,
                                'content_type': 'application/gzip'
                                }
            assets.append(no_release_assets_data)

        return assets

    async def get_latest_releases(self, repositories: dict) -> dict:
        """Runs get_release() asynchronously for each repository.

        Args:
            repositories (dict): dict of repositories and tags in Github's standard username/repository notation
            example (dict): {repo : tag, ...}

        Returns:
            dict: A dictionary containing assets from each repository
        """

        releases: dict[str, list] = {}
        releases['tools'] = []

        results: list = await asyncio.gather(*[self.__get_release(repository, tag) for repository, tag in repositories.items()])

        releases['tools'] = [asset for result in results for asset in result]

        return releases

    async def __get_patches_json(self, repository: str, tag: str = "latest") -> dict:
        """Get revanced-patches repository's README.md.
           
           args:
               repository (str): Github's standard username/repository notation
               tag (str): lateset(default)/ prerelease/ recent/ tag_name
                          see get_tag_release() for more details.

        Returns:
           dict: JSON content
        """

        release_dict = await self.get_tag_release(repository, tag)
        for asset in release_dict['assets']:
            if asset['name'] == "patches.json":
                return await self.httpx_client.get(asset['browser_download_url']).json()

    async def get_patches_json(self, repository: str, tag: str = "latest") -> dict:
        """Get patches.json from revanced-patches repository.
           
           args:
               repository (str): Github's standard username/repository notation
               tag (str): lateset(default), prerelease, recent, tag_name
                            see get_tag_release() for more details.

        Returns:
            dict: Patches available for a given app
        """

        patches: dict = await self.__get_patches_json(repository, tag)

        return patches

    async def __get_contributors(self, repository: str) -> list:
        """Get contributors from a given repository.

        Args:
           repository (str): Github's standard username/repository notation

        Returns:
           list: a list of dictionaries containing the repository's contributors
        """

        keep: set = {'login', 'avatar_url', 'html_url', 'contributions'}

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

        async for key, value in a.zip(revanced_repositories, results):
            data = {'name': key, 'contributors': value}
            contributors['repositories'].append(data)

        return contributors

    async def get_commits(self, repository: str, current_version: str, target_tag: str = "latest") -> list:
        """Get commit history from a given repository.

        Args:
            repository (str): Repository name
            current_version (str): current version(vx.x.x) installed
            target_tag (str): lateset(default), prerelease, recent, tag_name

        Returns:
            list: list containing the repository's commits between version
        """
        def to_numeric(string: str) -> str:
            if not string.isnumeric():
                numeric_str = ""
                for char in string:
                    if char.isdigit():
                        numeric_str += char
                return numeric_str
            return string

        def check_greater(check_string: str, check_with: str) -> bool :
            check_string = to_numeric(check_string)
            check_with = to_numeric(check_with)
            diff = abs(len(check_string) - len(check_with))

            if len(check_string) > len(check_with):
                check_with += "0"*diff
            elif len(check_string) < len(check_with):
                check_string += "0"*diff

            if int(check_string) > int(check_with):
                return True
            if int(check_string) < int(check_with):
                return False
            return None

        releases = await self.httpx_client.get(f"https://api.github.com/repos/{repository}/releases").json()
        target_release = await self.get_tag_release(repository, target_tag)
        target_prerelease = target_release['prerelease']
        target_version = to_numeric(target_release['tag_name'])

        def cleanup(body: str) ->list:
            #need more cleanups
            body = list(filter(lambda x :True if(x!="") else False, body.splitlines()))
            body.append("")
            return body

        commits = []
        for release in releases:
            if check_greater(target_version, current_version):
                if check_greater(release['tag_name'], current_version):
                    if check_greater(target_version, release['tag_name']) in (True, None):
                        if target_prerelease:
                            if release['prerelease']:
                                commits.extend(cleanup(release['body']))

                        elif not release['prerelease']:
                            commits.extend(cleanup(release['body']))

            elif check_greater(current_version, target_version):
                if check_greater(release['tag_name'], target_version) == None:
                    commits.extend(cleanup(release['body']))
                    break

            else:
                break

        return commits
