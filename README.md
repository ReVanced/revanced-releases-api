![License: AGPLv3](https://img.shields.io/github/license/alexandreteles/revanced-releases-api)
![GitHub last commit](https://img.shields.io/github/last-commit/alexandreteles/revanced-releases-api)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alexandreteles/revanced-releases-api/Main%20build)

# ReVanced Releases API

This is a simple API that returns the latest ReVanced releases.

## Usage

The API is available at [https://revanced-releases-api.afterst0rm.xyz/](https://revanced-releases-api.afterst0rm.xyz/).

For development purposes, you can run the API locally by cloning this repository and running `docker-compose up` or `docker-compose up --build` if you want to rebuild the image. Optionally you can run the application without Docker by running `pip -U install -r ./requirements.txt` and `python ./main.py`. Remember to set the environment variable `GITHUB_TOKEN` to a valid token if you want to run the API locally.

### API Endpoints

* [apps](https://revanced-releases-api.afterst0rm.xyz/apps) - Returns all currently patchable apps
* [tools](https://revanced-releases-api.afterst0rm.xyz/tools) - Returns the latest version of all ReVanced tools and Vanced MicroG
* [patches](https://revanced-releases-api.afterst0rm.xyz/patches) - Returns the latest version of all ReVanced patches

## Contributing

If you want to contribute to this project, feel free to open a pull request or an issue. We don't do much here, so it's pretty easy to contribute.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [ReVanced Team](https://github.com/revanced/) for making such a great project
