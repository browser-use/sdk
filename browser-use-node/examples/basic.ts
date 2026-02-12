/**
 * Basic task — run a task and get the result.
 */
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  // Option 1: Quick — run() returns a TaskHandle you can await
  const handle = client.run({
    task: "Search for the top 10 Hacker News posts and return the title and url.",
  });
  const result = await handle.complete();
  console.log(result.output);

  // Option 2: Direct — use the tasks resource
  const task = await client.tasks.create({
    task: "What is the current price of Bitcoin?",
  });
  console.log("Task created:", task.id);

  // Poll for result
  const finished = await client.tasks.get(task.id);
  console.log(finished.output);
}

main();
