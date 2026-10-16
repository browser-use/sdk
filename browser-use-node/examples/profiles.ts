/**
 * Profiles — persist browser state (cookies, logins) across runs.
 *
 * Create a profile once, then reuse it. Login state carries over.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

/** Run a task, stop its browsers (which saves the profile), and return the result. */
async function runTask(client: BrowserUse, task: string, profileId: string) {
  const run = await client.runs.create({ task, browserSettings: { profileId } });
  let result;
  try {
    result = await client.runs.waitForCompletion(run.id);
  } finally {
    // sessionId is the agent session, not a browser id.
    const browsers = await client.browsers.list({ agentSessionId: run.sessionId, filterBy: "active" });
    for (const b of browsers.items) await client.browsers.stop(b.id);
  }
  if (result.status !== "completed") throw new Error(`Run ${result.status}: ${result.error}`);
  return result.result;
}

async function main() {
  const client = new BrowserUse();

  // Create a named profile
  const profile = await client.profiles.create({ name: "My LinkedIn Profile" });
  console.log("Profile created:", profile.id);

  try {
    // First run: log in (profile saves the cookies)
    await runTask(client, "Go to linkedin.com and log in with my credentials", profile.id);

    // Later run: already logged in from saved profile
    const result = await runTask(client, "Go to my LinkedIn profile and get my connection count", profile.id);
    console.log("Result:", result);

    // List all profiles
    const profiles = await client.profiles.list();
    console.log(`You have ${profiles.totalItems} profiles`);
  } finally {
    await client.profiles.delete(profile.id);
  }
}

main();
