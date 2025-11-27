export default defineEventHandler(async (event) => {
	const { apiKeyFlag } = useRuntimeConfig(event)
	try {
		const data = await $fetch(
			"http://localhost:8080/weather/latest",
			{
				headers: {
					"x-api-key-flag":
						apiKeyFlag,
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
