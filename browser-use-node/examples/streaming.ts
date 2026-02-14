/**
 * Streaming — monitor task progress in real time.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  for await (const step of client.run(
    "Go to wikipedia.org and find the featured article of the day.",
  )) {
    console.log(`[${step.number}] ${step.nextGoal} — ${step.url}`);
  }

  const task = client.run("Summarize the wikipedia.org main page.");
  for await (const step of task) {
    console.log(`[${step.number}] ${step.nextGoal} — ${step.url}`);
  }
  console.log("\nOutput:", task.result!.output);
}

main();
