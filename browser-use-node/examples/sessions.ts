/**
 * Sessions — run multiple tasks in the same browser session.
 *
 * Sessions let you chain tasks that share browser state (cookies, tabs, etc).
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  // Create a session with a UK proxy
  const session = await client.sessions.create({
    proxyCountryCode: "uk",
  });
  console.log(`Session: ${session.id}`);
  console.log(`Watch live: ${session.liveUrl}`);

  // Run a task in this session
  const output1 = await client.run(
    "Go to google.co.uk and search for 'browser automation'",
    { sessionId: session.id },
  );
  console.log("Task 1:", output1);

  // Run another task in the same session (browser state is preserved)
  const output2 = await client.run(
    "Click on the first search result and summarize the page",
    { sessionId: session.id },
  );
  console.log("Task 2:", output2);

  // Clean up
  await client.sessions.stop(session.id);
  await client.sessions.delete(session.id);
}

main();
