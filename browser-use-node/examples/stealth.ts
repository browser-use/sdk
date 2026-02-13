/**
 * Stealth mode — use proxies for geo-specific browsing.
 *
 * Every session gets a residential proxy. You can choose the country.
 * Without a session, tasks auto-create one with a US proxy.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  // Auto-session (US proxy by default)
  const usOutput = await client.run(
    "Go to whatismyipaddress.com and tell me my location",
  );
  console.log("US proxy:", usOutput);

  // Custom proxy — Germany
  const deSession = await client.sessions.create({
    proxyCountryCode: "de",
  });
  const deOutput = await client.run(
    "Go to whatismyipaddress.com and tell me my location",
    { sessionId: deSession.id },
  );
  console.log("DE proxy:", deOutput);

  await client.sessions.stop(deSession.id);
}

main();
