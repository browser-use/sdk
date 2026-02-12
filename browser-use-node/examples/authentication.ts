/**
 * Authentication — use profiles to stay logged in across sessions.
 *
 * 1. Create a profile
 * 2. Log in once in a session with that profile
 * 3. Future sessions with the same profile are already logged in
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  const PROFILE_ID = "your-profile-id"; // Create one with client.profiles.create()

  // Create a session with your profile (inherits saved cookies/login state)
  const session = await client.sessions.create({ profileId: PROFILE_ID });

  // Run an authenticated task
  const handle = client.run({
    task: "Go to my LinkedIn profile and get my connection count",
    sessionId: session.id,
  });
  const result = await handle.complete();
  console.log(result.output);

  await client.sessions.stop(session.id);
}

main();
