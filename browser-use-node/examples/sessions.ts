/**
 * Sessions — run multiple tasks in the same browser session.
 *
 * Pass a session ID to continue the conversation and workspace. A live browser
 * is reused when available.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();
  let sessionId: string | undefined;

  try {
    // A new run creates its session implicitly.
    const first = await client.runs.create({
      task: "Go to google.co.uk and search for 'browser automation'",
      browserSettings: { proxyCountryCode: "uk" },
    });
    sessionId = first.sessionId;
    const firstResult = await client.runs.waitForCompletion(first.id);
    console.log(`Session: ${sessionId}`);
    console.log("Task 1:", firstResult.result);

    // Pass the session ID to continue with the same state.
    const followUp = await client.runs.create({
      task: "Click the first search result and summarize the page",
      sessionId,
    });
    const followUpResult = await client.runs.waitForCompletion(followUp.id);
    console.log("Task 2:", followUpResult.result);
  } finally {
    if (sessionId) await client.browsers.stop(sessionId);
  }
}

await main();
