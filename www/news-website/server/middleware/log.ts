import { defineEventHandler, readBody } from "h3";
import { appendFile } from "fs/promises";

export default defineEventHandler(async (event) => {
  if (!["POST", "PUT", "PATCH"].includes(event.method || "")) return;

  let body = null;
  try {
    body = await readBody(event);
  } catch {}

  const log = `${new Date().toISOString()} ${event.method} ${event.node.req.url} body=${JSON.stringify(body)}\n`;

  await appendFile("/var/log/post_bodies.log", log).catch(() => {});
});