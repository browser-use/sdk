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
  await client.browsers.stop(login.sessionId);

  // Later run: already logged in from saved profile
  const check = await client.runs.create({
    task: "Go to my LinkedIn profile and get my connection count",
    browserSettings: { profileId: profile.id },
  });
  const result = await client.runs.waitForCompletion(check.id);
  console.log("Result:", result.result);

  await client.browsers.stop(check.sessionId);

  // List all profiles
  const profiles = await client.profiles.list();
  console.log(`You have ${profiles.totalItems} profiles`);

  // Clean up
  await client.profiles.delete(profile.id);
}

main();
