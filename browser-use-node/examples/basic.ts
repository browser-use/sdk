/**
 * Basic task — run a task and get the result.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";

async function main() {
  const client = new BrowserUse();

  const run = await client.runs.create({
    task: "Search for the top 10 Hacker News posts and return the title and URL.",
  });
  const result = await client.runs.waitForCompletion(run.id);
  console.log(result.result);
}

await main();
