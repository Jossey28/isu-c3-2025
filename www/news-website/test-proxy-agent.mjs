#!/usr/bin/env node

/**
 * Test script to verify undici's ProxyAgent works
 * Run with: node test-proxy-agent.mjs
 */

import { ProxyAgent, setGlobalDispatcher } from 'undici';

const proxyUrl = "http://199.100.16.100:3128";

console.log("=== ProxyAgent Test Script ===");
console.log("Node version:", process.version);
console.log("Proxy URL:", proxyUrl);
console.log("\n");

// Set ProxyAgent as global dispatcher
console.log("Setting up ProxyAgent...");
try {
  const proxyAgent = new ProxyAgent(proxyUrl);
  setGlobalDispatcher(proxyAgent);
  console.log("✅ ProxyAgent configured successfully");
} catch (error) {
  console.log("❌ Failed to configure ProxyAgent:", error.message);
  process.exit(1);
}

console.log("\n");

// Test 1: Iconify API
console.log("Test 1: Fetching from api.iconify.design...");
try {
  const response = await fetch("https://api.iconify.design/icomoon-free.json?icons=rss");
  const data = await response.json();
  console.log("✅ SUCCESS: Iconify fetch completed");
  console.log("  Status:", response.status);
  console.log("  Data preview:", JSON.stringify(data).substring(0, 100) + "...");
} catch (error) {
  console.log("❌ FAILED: Iconify fetch failed");
  console.log("  Error:", error.message);
  console.log("  Cause:", error.cause?.message || "N/A");
  console.log("  Code:", error.cause?.code || "N/A");
}

console.log("\n");

// Test 2: Google Fonts
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

console.log("\n");

// Test 3: Font Share
console.log("Test 3: Fetching from api.fontshare.com...");
try {
  const response = await fetch("https://api.fontshare.com/v2/fonts?offset=0&limit=5");
  console.log("✅ SUCCESS: Font Share fetch completed");
  console.log("  Status:", response.status);
} catch (error) {
  console.log("❌ FAILED: Font Share fetch failed");
  console.log("  Error:", error.message);
}

console.log("\n=== Test Complete ===");
console.log("\nResult:");
console.log("- If all tests succeeded: ProxyAgent works! Build should succeed");
console.log("- If all tests failed: ProxyAgent can't connect through proxy");
console.log("  → May need to disable external font/icon fetching entirely");
