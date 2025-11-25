import { defineNuxtPlugin } from '#app'
// Collections packaged by Iconify (install with npm/yarn)
// These JSON files contain the icon vectors for the given collection prefix.
import icomoon from '@iconify-json/icomoon-free/collection.json'
import wi from '@iconify-json/wi/collection.json'

// `addCollection` is provided by @iconify/vue to register collections locally
import { addCollection } from '@iconify/vue'

export default defineNuxtPlugin(() => {
  try {
    // Register collections so Iconify resolves icons locally and does not fetch at runtime
    addCollection(icomoon as any)
    addCollection(wi as any)
  } catch (e) {
    // Log but do not crash the app — if registration fails, runtime will still attempt fetch
    // This helps debugging in environments where packages are not yet installed
    // eslint-disable-next-line no-console
    console.warn('[iconify] failed to register collections locally:', e)
  }
})
