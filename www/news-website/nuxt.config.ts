// https://nuxt.com/docs/api/configuration/nuxt-config
import dotenv from "dotenv";
import { ProxyAgent, setGlobalDispatcher } from "undici";
dotenv.config();

// Set proxy for build-time fetches (fonts, icons, etc.)
// Node v22's undici doesn't respect env vars by default - must use ProxyAgent
const proxyUrl = "http://199.100.16.100:3128";

try {
	const proxyAgent = new ProxyAgent(proxyUrl);
	setGlobalDispatcher(proxyAgent);
} catch (error) {
	process.env.HTTPS_PROXY = proxyUrl;
	process.env.https_proxy = proxyUrl;
	process.env.HTTP_PROXY = proxyUrl;
	process.env.http_proxy = proxyUrl;
}

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
		public: {
		livestreamAddress: process.env.NUXT_LIVESTREAM_ADDRESS,
		},
	},
});
