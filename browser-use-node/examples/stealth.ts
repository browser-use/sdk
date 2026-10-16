/**
 * Stealth mode — use proxies for geo-specific browsing.
 *
 * Every run's browser gets a residential proxy. You can choose the country;
 * the default is US.
 */
import "dotenv/config";
import { BrowserUse, type RunCreateBody } from "browser-use-sdk/v4";

const TASK = "Go to whatismyipaddress.com and tell me my location";

/** Run TASK, stop its browsers, and return the result. */
async function runTask(client: BrowserUse, browserSettings?: RunCreateBody["browserSettings"]) {
  const run = await client.runs.create({ task: TASK, browserSettings });
  let result;
  try {
    result = await client.runs.waitForCompletion(run.id);
  } finally {
    // sessionId is the agent session; each of its browsers has its own id.
    const browsers = await client.browsers.list({ agentSessionId: run.sessionId, filterBy: "active" });
    for (const b of browsers.items) await client.browsers.stop(b.id);
  }
  if (result.status !== "completed") throw new Error(`Run ${result.status}: ${result.error}`);
  return result.result;
}

async function main() {
  const client = new BrowserUse();

  // Default proxy (US)
  console.log("US proxy:", await runTask(client));

  // Custom proxy — Germany
  console.log("DE proxy:", await runTask(client, { proxyCountryCode: "de" }));
}

main();
