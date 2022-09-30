# ReVanced Releases API

![License: AGPLv3](https://img.shields.io/github/license/revanced/revanced-releases-api)
![GitHub last commit](https://img.shields.io/github/last-commit/revanced/revanced-releases-api)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/revanced/revanced-releases-api/Build%20dev%20branch)

This is a simple API that returns the latest ReVanced releases, patches and contributors.

## Usage

The API is available at [https://revanced-releases-api.afterst0rm.xyz/](https://revanced-releases-api.afterst0rm.xyz/).

You can deploy your own instance by cloning this repository, editing the `docker-compose.yml` file to include your GitHub token and running `docker-compose up` or `docker-compose up --build` if you want to build the image locally instead of pulling from GHCR. Optionally you can run the application without Docker by running `poetry install` and `poetry run ./run.sh`. In this case, you'll also need a redis server and setup the following environment variables on your system.

| Variable               | Description                           |
| ---------------------- | ------------------------------------- |
| `GITHUB_TOKEN`         | Your GitHub token.                    |
| `REDIS_URL`            | The hostname/IP of your redis server. |
| `REDIS_PORT`           | The port of your redis server.        |
| `HYPERCORN_HOST`       | The hostname/IP of the API.           |
| `HYPERCORN_PORT`       | The port of the API.                  |
| `HYPERCORN_LOG_LEVEL`  | The log level of the API.             |
| `SENTRY_DSN`           | The DSN of your Sentry instance.      |

Please note that there are no default values for any of these variables.

If you don't have a Sentry instance, we recommend using [GlitchTip](https://glitchtip.com/).

### API Endpoints

* [tools](https://revanced-releases-api.afterst0rm.xyz/tools) - Returns the latest version of all ReVanced tools and Vanced MicroG
* [patches](https://revanced-releases-api.afterst0rm.xyz/patches) - Returns the latest version of all ReVanced patches
* [contributors](https://revanced-releases-api.afterst0rm.xyz/contributors) - Returns contributors for all ReVanced projects

## Contributing

If you want to contribute to this project, feel free to open a pull request or an issue. We don't do much here, so it's pretty easy to contribute.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.
