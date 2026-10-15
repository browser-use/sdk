/**
 * Streaming — monitor run progress by polling its events.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();

  const run = await client.runs.create({
    task: "Go to wikipedia.org and find the featured article of the day.",
  });

  // Read status before events so the last page is fetched after the run ended.
  let after: number | undefined;
  while (true) {
    const { status } = await client.runs.status(run.id);
    const page = await client.runs.events(run.id, { after });
    for (const event of page.events) {
      console.log(event.type, event.data);
    }
    after = page.nextAfter ?? after;

    if (["completed", "failed", "cancelled"].includes(status) && !page.hasMore) break;
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }

  const result = await client.runs.get(run.id);
  console.log("\nOutput:", result.result);
}

main();
