/**
 * Authentication — use profiles to stay logged in across runs.
 *
 * 1. Create a profile
 * 2. Log in once in a run with that profile
 * 3. Future runs with the same profile are already logged in
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();

  const PROFILE_ID = "your-profile-id"; // Create one with client.profiles.create()

  // Run with your profile (inherits saved cookies/login state)
  const run = await client.runs.create({
    task: "Go to my LinkedIn profile and get my connection count",
    browserSettings: { profileId: PROFILE_ID },
  });
  let result;
  try {
    result = await client.runs.waitForCompletion(run.id);
  } finally {
    // sessionId is the agent session; each of its browsers has its own id.
    const browsers = await client.browsers.list({ agentSessionId: run.sessionId, filterBy: "active" });
    for (const b of browsers.items) await client.browsers.stop(b.id);
  }
  if (result.status !== "completed") throw new Error(`Run ${result.status}: ${result.error}`);
  console.log(result.result);
}

main();
