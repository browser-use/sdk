/**
 * Sessions — run multiple tasks in the same browser session.
 *
 * Sessions let you chain tasks that share browser state (cookies, tabs, etc).
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  // Create a session with a UK proxy
  const session = await client.sessions.create({
    proxyCountryCode: "uk",
  });
  console.log(`Session: ${session.id}`);
  console.log(`Watch live: ${session.liveUrl}`);

  // Run a task in this session
  const handle = client.run({
    task: "Go to google.co.uk and search for 'browser automation'",
    sessionId: session.id,
  });
  const result = await handle.complete();
  console.log("Task 1:", result.output);

  // Run another task in the same session (browser state is preserved)
  const handle2 = client.run({
    task: "Click on the first search result and summarize the page",
    sessionId: session.id,
  });
  const result2 = await handle2.complete();
  console.log("Task 2:", result2.output);

  // Clean up
  await client.sessions.stop(session.id);
  await client.sessions.delete(session.id);
}

main();
