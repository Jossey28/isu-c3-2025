#!/usr/bin/env node

/**
 * Test script to verify Node's fetch uses proxy configuration
 * Run with: node test-proxy.mjs
 */

// Set proxy env vars
const proxyUrl = "http://199.100.16.100:3128";
process.env.HTTPS_PROXY = proxyUrl;
process.env.https_proxy = proxyUrl;
process.env.HTTP_PROXY = proxyUrl;
process.env.http_proxy = proxyUrl;

console.log("=== Proxy Test Script ===");
console.log("Node version:", process.version);
console.log("Proxy configured:", proxyUrl);
console.log("Environment variables:");
console.log("  HTTPS_PROXY:", process.env.HTTPS_PROXY);
console.log("  https_proxy:", process.env.https_proxy);
console.log("  HTTP_PROXY:", process.env.HTTP_PROXY);
console.log("  http_proxy:", process.env.http_proxy);
console.log("\n");

// Test 1: Simple HTTPS fetch
console.log("Test 1: Fetching from api.iconify.design...");
try {
  const response = await fetch("https://api.iconify.design/icomoon-free.json?icons=rss");
  const data = await response.json();
  console.log("✅ SUCCESS: Fetch completed");
  console.log("  Status:", response.status);
  console.log("  Data preview:", JSON.stringify(data).substring(0, 100) + "...");
} catch (error) {
  console.log("❌ FAILED: Fetch failed");
  console.log("  Error:", error.message);
  console.log("  Cause:", error.cause?.message || "N/A");
  console.log("  Code:", error.cause?.code || "N/A");
}

console.log("\n");

// Test 2: Google Fonts API (another endpoint that failed in your build)
console.log("Test 2: Fetching from fonts.google.com...");
try {
  const response = await fetch("https://fonts.google.com/metadata/fonts", {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  console.log("✅ SUCCESS: Google Fonts fetch completed");
  console.log("  Status:", response.status);
} catch (error) {
  console.log("❌ FAILED: Google Fonts fetch failed");
  console.log("  Error:", error.message);
  console.log("  Cause:", error.cause?.message || "N/A");
}

console.log("\n=== Test Complete ===");
console.log("\nDiagnosis:");
console.log("- If both tests succeeded: Proxy is working correctly");
console.log("- If both tests failed: Node's fetch (undici) is NOT using proxy env vars");
console.log("  → Solution: Use global-agent or undici ProxyAgent explicitly");
console.log("- If mixed results: Some endpoints may be blocked differently");
