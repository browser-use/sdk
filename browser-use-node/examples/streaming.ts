/**
 * Streaming — monitor task progress in real time.
 */
import { BrowserUse } from "browser-use-sdk";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  const handle = client.run({
    task: "Go to wikipedia.org and find the featured article of the day.",
  });

  // stream() yields TaskStatusView on each poll
  for await (const status of handle.stream({ interval: 2_000 })) {
    console.log(`[${status.status}] Step output:`, status.output ?? "(running...)");
  }

  // After the stream ends, get the full result
  const created = await handle.created();
  const result = await client.tasks.get(created.id);
  console.log("\nFinal output:", result.output);
}

main();
