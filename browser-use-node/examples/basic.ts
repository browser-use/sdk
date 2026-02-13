/**
 * Basic task — run a task and get the result.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  // Quick — run() with await returns the output string directly
  const output = await client.run(
    "Search for the top 10 Hacker News posts and return the title and url.",
  );
  console.log(output);

  // You can also access the full TaskView via .result after awaiting
  const run = client.run("What is the current price of Bitcoin?");
  const output2 = await run;
  console.log(output2);
  console.log("Task ID:", run.result!.id);
}

main();
