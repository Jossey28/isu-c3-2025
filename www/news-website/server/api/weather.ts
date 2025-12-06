import { defineEventHandler } from 'h3';
import { Agent } from 'https'; // Import Node's HTTPS agent



export default defineEventHandler(async (event) => {
    const { apiKeyFlag } = useRuntimeConfig(event)
    
    // Create an agent that ignores self-signed certificate errors
    const httpsAgent = new Agent({ rejectUnauthorized: false });

    try {
        const data = await $fetch(
            "https://localhost:8080/weather/latest",
            {
                // Pass the custom agent here
                agent: httpsAgent, 
                headers: {
                    "x-api-key-flag": apiKeyFlag,
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