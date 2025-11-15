// https://nuxt.com/docs/api/configuration/nuxt-config
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
		public: {
			apiKeyFlag: process.env.NUXT_API_KEY_FLAG,
			livestreamAddress: process.env.NUXT_LIVESTREAM_ADDRESS,
		},
	},
});
