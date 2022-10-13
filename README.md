# ReVanced Releases API

![License: AGPLv3](https://img.shields.io/github/license/revanced/revanced-releases-api)
![GitHub last commit](https://img.shields.io/github/last-commit/revanced/revanced-releases-api)
![GitHub Workflow Status](https://github.com/revanced/revanced-releases-api/actions/workflows/dev.yml/badge.svg)

This is a simple API that returns the latest ReVanced releases, patches and contributors.

## Usage

The API is available at [https://releases.rvcd.win/](https://releases.rvcd.win/).

You can deploy your own instance by cloning this repository, editing the `docker-compose.yml` file to include your GitHub token and running `docker-compose up` or `docker-compose up --build` if you want to build the image locally instead of pulling from GHCR. Optionally you can run the application without Docker by running `poetry install` and `poetry run ./run.sh`. In this case, you'll also need a redis server and setup the following environment variables on your system.

| Variable               | Description                           |
| ---------------------- | ------------------------------------- |
| `GITHUB_TOKEN`         | Your GitHub token.                    |
| `REDIS_URL`            | The hostname/IP of your redis server. |
| `REDIS_PORT`           | The port of your redis server.        |
| `HYPERCORN_HOST`       | The hostname/IP of the API.           |
| `HYPERCORN_PORT`       | The port of the API.                  |
| `SENTRY_DSN`           | The DSN of your Sentry instance.      |

Please note that there are no default values for any of these variables.

If you don't have a Sentry instance, we recommend using [GlitchTip](https://glitchtip.com/).

### API Endpoints

* [tools](https://releases.rvcd.win/tools) - Returns the latest version of all ReVanced tools and Vanced MicroG
* [patches](https://releases.rvcd.win/patches) - Returns the latest version of all ReVanced patches
* [contributors](https://releases.rvcd.win/contributors) - Returns contributors for all ReVanced projects
* [announcement](https://releases.rvcd.win/announcement) - Returns the latest announcement for the ReVanced projects

## Clients

The API has no concept of users. It is meant to be used by clients, such as the [ReVanced Manager](https://github.com/revanced/revanced-manager).

When the API is deployed for the first time it'll create a new client with admin permissions. The credentials can be found at the log console or in the file `admin_info.json` in the root directory of the project. Only admin clients can create, edit and delete other clients. If you're going to use any of the authenticated endpoints, you'll need to create a client and use its credentials. Please follow the API documentation for more information.

## Authentication

The API uses [PASETO](https://paseto.io/) tokens for authorization. To authenticate, you need to send a POST request to `/auth` with the following JSON body:

```json
{
  "id": "your_client_id",
  "secret": "your_client_secret"
}
```

The API will answer with a PASETO token and a refresh token that you can use to authorize your requests. You can use the token in the `Authorization` header of your requests, like this:

```
Authorization: Bearer <token>
```

That token will be valid for 24 hours. After that, you'll need to refresh it by sending a POST request to `/auth/refresh` with your `refresh_token` in the `Authorization` header.

Refresh tokens are valid for 30 days. After that, you'll need to authenticate again and get new tokens.

Some endpoints might require fresh tokens, forcing you to authenticate.

## Contributing

If you want to contribute to this project, feel free to open a pull request or an issue. We don't do much here, so it's pretty easy to contribute.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.
