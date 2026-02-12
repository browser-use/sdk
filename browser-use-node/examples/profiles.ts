/**
 * Profiles — persist browser state (cookies, logins) across sessions.
 *
 * Create a profile once, then reuse it. Login state carries over.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  // Create a named profile
  const profile = await client.profiles.create({ name: "My LinkedIn Profile" });
  console.log("Profile created:", profile.id);

  // First session: log in (profile saves the cookies)
  const session1 = await client.sessions.create({ profileId: profile.id });
  const loginTask = client.run({
    task: "Go to linkedin.com and log in with my credentials",
    sessionId: session1.id,
  });
  await loginTask.complete();
  await client.sessions.stop(session1.id);

  // Later session: already logged in from saved profile
  const session2 = await client.sessions.create({ profileId: profile.id });
  const dataTask = client.run({
    task: "Go to my LinkedIn profile and get my connection count",
    sessionId: session2.id,
  });
  const result = await dataTask.complete();
  console.log("Result:", result.output);

  await client.sessions.stop(session2.id);

  // List all profiles
  const profiles = await client.profiles.list();
  console.log(`You have ${profiles.totalItems} profiles`);

  // Clean up
  await client.profiles.delete(profile.id);
}

main();
