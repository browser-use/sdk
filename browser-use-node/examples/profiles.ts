/**
 * Profiles — persist browser state (cookies, logins) across runs.
 *
 * Create a profile once, then reuse it. Login state carries over.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();

  // Create a named profile
  const profile = await client.profiles.create({ name: "My LinkedIn Profile" });
  console.log("Profile created:", profile.id);

  // First run: log in (profile saves the cookies)
  const login = await client.runs.create({
    task: "Go to linkedin.com and log in with my credentials",
    browserSettings: { profileId: profile.id },
  });
  await client.runs.waitForCompletion(login.id);
  // Stopping the browser saves the profile. sessionId is the agent session, not a browser id.
  const loginBrowsers = await client.browsers.list({ agentSessionId: login.sessionId, filterBy: "active" });
  for (const b of loginBrowsers.items) await client.browsers.stop(b.id);

  // Later run: already logged in from saved profile
  const check = await client.runs.create({
    task: "Go to my LinkedIn profile and get my connection count",
    browserSettings: { profileId: profile.id },
  });
  const result = await client.runs.waitForCompletion(check.id);
  console.log("Result:", result.result);

  const checkBrowsers = await client.browsers.list({ agentSessionId: check.sessionId, filterBy: "active" });
  for (const b of checkBrowsers.items) await client.browsers.stop(b.id);

  // List all profiles
  const profiles = await client.profiles.list();
  console.log(`You have ${profiles.totalItems} profiles`);

  // Clean up
  await client.profiles.delete(profile.id);
}

main();
