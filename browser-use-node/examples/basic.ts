/**
 * Basic task — run a task and get the result.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  const result = await client.run(
    "Search for the top 10 Hacker News posts and return the title and url.",
  );
  console.log(result.output);
  console.log(result.id, result.status, result.steps.length);
}

main();
