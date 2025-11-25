// https://nuxt.com/docs/api/configuration/nuxt-config
import dotenv from "dotenv";
import { ProxyAgent, setGlobalDispatcher } from "undici";
dotenv.config();

// Set proxy for build-time fetches (fonts, icons, etc.)
// Node v22's undici doesn't respect env vars by default - must use ProxyAgent
const proxyUrl = "http://199.100.16.100:3128";

console.log("=== Proxy Configuration (undici ProxyAgent) ===");
console.log("Proxy URL:", proxyUrl);

try {
	const proxyAgent = new ProxyAgent(proxyUrl);
	setGlobalDispatcher(proxyAgent);
	console.log("✅ Global dispatcher set to ProxyAgent");
} catch (error) {
	console.error("❌ Failed to set ProxyAgent:", error.message);
	console.log("Falling back to environment variables...");
	process.env.HTTPS_PROXY = proxyUrl;
	process.env.https_proxy = proxyUrl;
	process.env.HTTP_PROXY = proxyUrl;
	process.env.http_proxy = proxyUrl;
}

console.log("===========================================\n");

export default defineNuxtConfig({
	compatibilityDate: "2025-07-15",
	devtools: { enabled: true },

	modules: [
		"@nuxt/content",
		"@nuxt/eslint",
		"@nuxt/image",
		"@nuxt/scripts",
		"@nuxt/ui",
	],
	css: ["~/assets/css/main.css"],
	runtimeConfig: {
		// private runtime config (available only server-side)
		databasePassword: process.env.NUXT_DATABASE_PASSWORD,
		databaseUser: process.env.NUXT_DATABASE_USER,
		apiKeyFlag: process.env.NUXT_API_KEY_FLAG,
		livestreamAddress: process.env.NUXT_LIVESTREAM_ADDRESS,
	},
});
