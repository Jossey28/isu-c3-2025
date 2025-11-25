import { defineNuxtPlugin } from '#app'

/**
 * Server-only plugin that configures Node's global fetch to use a proxy.
 * This is a backup solution in case icon collections fail to load or new icons are added.
 * The .server.ts suffix ensures this only runs on the server, not in the browser.
 */
export default defineNuxtPlugin(() => {
  // Set proxy for Node's built-in fetch (undici)
  // These env vars are used by undici and other Node HTTP clients
  const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || 'http://199.100.16.100:3128'
  
  if (!process.env.HTTPS_PROXY && !process.env.https_proxy) {
    // Set the env var so undici and other clients use the proxy
    process.env.HTTPS_PROXY = proxyUrl
    process.env.https_proxy = proxyUrl
    // Also set HTTP_PROXY for completeness
    process.env.HTTP_PROXY = proxyUrl
    process.env.http_proxy = proxyUrl
    
    // eslint-disable-next-line no-console
    console.info(`[proxy-config] Set proxy for Node fetch: ${proxyUrl}`)
  }
  
  // For older Node versions or alternative fetch libraries, you might need global-agent
  // Uncomment the following if the above doesn't work and install global-agent:
  // import { bootstrap } from 'global-agent'
  // process.env.GLOBAL_AGENT_HTTP_PROXY = proxyUrl
  // bootstrap()
})
