/**
 * Stealth mode — use proxies for geo-specific browsing.
 *
 * Every run's browser gets a residential proxy. You can choose the country;
 * the default is US.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();

  // Default proxy (US)
  const us = await client.runs.create({
    task: "Go to whatismyipaddress.com and tell me my location",
  });
  console.log("US proxy:", (await client.runs.waitForCompletion(us.id)).result);

  // Custom proxy — Germany
  const de = await client.runs.create({
    task: "Go to whatismyipaddress.com and tell me my location",
    browserSettings: { proxyCountryCode: "de" },
  });
  console.log("DE proxy:", (await client.runs.waitForCompletion(de.id)).result);

  await client.browsers.stop(us.sessionId);
  await client.browsers.stop(de.sessionId);
}

main();
