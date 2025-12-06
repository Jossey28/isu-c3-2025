export default defineEventHandler(async (event) => {
	const { apiKeyFlag } = useRuntimeConfig(event)
	try {
		const data = await $fetch(
			"https://localhost:8080/weather/latest",
			{
				headers: {
					"x-api-key-flag":
						apiKeyFlag,
					"user-agent": "WWW-NEWS-Website/1.0",
				},
			},
		);

		return data;
	} catch (err) {
		console.error("Error fetching weather:", err);
		throw createError({
			statusCode: 500,
			statusMessage: "Failed to fetch weather data",
		});
	}
});
