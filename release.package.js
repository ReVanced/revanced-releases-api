module.exports = {
	branches: ["main"],
	plugins: [
		[
			"@codedependant/semantic-release-docker",
			{
				dockerTags: [process.env.IMAGE_TAG],
				dockerImage: process.env.IMAGE_NAME,
				dockerFile: "Dockerfile",
				dockerRegistry: "ghcr.io",
				dockerProject: "codedependant",
				dockerArgs: {
					API_TOKEN: true,
					RELEASE_DATE: new Date().toISOString(),
					RELEASE_VERSION: "{{next.version}}",
				},
			},
		],
	],
};
