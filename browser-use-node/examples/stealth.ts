/**
 * Stealth mode — use proxies for geo-specific browsing.
 *
 * Every session gets a residential proxy. You can choose the country.
 * Without a session, tasks auto-create one with a US proxy.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  // Auto-session (US proxy by default)
  const usTask = client.run({
    task: "Go to whatismyipaddress.com and tell me my location",
  });
  const usResult = await usTask.complete();
  console.log("US proxy:", usResult.output);

  // Custom proxy — Germany
  const deSession = await client.sessions.create({
    proxyCountryCode: "de",
  });
  const deTask = client.run({
    task: "Go to whatismyipaddress.com and tell me my location",
    sessionId: deSession.id,
  });
  const deResult = await deTask.complete();
  console.log("DE proxy:", deResult.output);

  await client.sessions.stop(deSession.id);
}

main();
