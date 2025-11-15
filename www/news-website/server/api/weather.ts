export default defineEventHandler(async (event) => {
	try {
		const data = await $fetch(
			"http://localhost:8080/weather/latest",
			{
				headers: {
					"x-api-key-flag":
						process.env.NUXT_API_KEY_FLAG,
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
