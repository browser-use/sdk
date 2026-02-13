/**
 * Streaming — monitor task progress in real time.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse();

  // for-await iterates TaskStepView objects as the task progresses
  for await (const step of client.run(
    "Go to wikipedia.org and find the featured article of the day.",
  )) {
    console.log(`[${step.number}] ${step.nextGoal} — ${step.url}`);
  }

  // After the loop ends, the task is complete.
  // To also get the final output, capture the run handle:
  const task = client.run("Summarize the wikipedia.org main page.");
  for await (const step of task) {
    console.log(`[${step.number}] ${step.nextGoal} — ${step.url}`);
  }
  console.log("\nFinal output:", task.result!.output);
}

main();
