# ReVanced Releases API

![License: AGPLv3](https://img.shields.io/github/license/alexandreteles/revanced-releases-api)
![GitHub last commit](https://img.shields.io/github/last-commit/alexandreteles/revanced-releases-api)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alexandreteles/revanced-releases-api/Main%20build)

This is a simple API that returns the latest ReVanced releases, patches and contributors.

## Usage

The API is available at [https://revanced-releases-api.afterst0rm.xyz/](https://revanced-releases-api.afterst0rm.xyz/).

You can deploy your own instance by cloning this repository, editing the `docker-compose.yml` file to include your GitHub token and running `docker-compose up` or `docker-compose up --build` if you want to build the image locally instead of pulling from Docker Hub. Optionally you can run the application without Docker by running `poetry install` and `poetry run ./main.py`. In this case, you'll also need a redis server and setup the `REDIS_URL`, `REDIS_PORT` and `GITHUB_TOKEN` environment variables on your system.

### API Endpoints

* [tools](https://revanced-releases-api.afterst0rm.xyz/tools) - Returns the latest version of all ReVanced tools and Vanced MicroG
* [patches](https://revanced-releases-api.afterst0rm.xyz/patches) - Returns the latest version of all ReVanced patches
* [contributors](https://revanced-releases-api.afterst0rm.xyz/contributors) - Returns contributors for all ReVanced projects

## Contributing

If you want to contribute to this project, feel free to open a pull request or an issue. We don't do much here, so it's pretty easy to contribute.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [ReVanced Team](https://github.com/revanced/) for making such a great project
