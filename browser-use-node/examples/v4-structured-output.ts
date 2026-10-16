/** Request V4 structured output with JSON Schema and validate it explicitly. */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk/v4";
import { z } from "zod";

const PageInfo = z.object({ title: z.string(), url: z.string() });
const client = new BrowserUse();
const created = await client.runs.create({
  task: "Open https://example.com and return its page title and URL.",
  outputSchema: z.toJSONSchema(PageInfo),
});
const run = await client.runs.waitForCompletion(created.id);
if (run.status !== "completed") {
  throw new Error(run.error ?? `Run ended with ${run.status}`);
}
// result remains the text answer; output is unknown until validated.
console.log(run.result);
if (run.output != null) {
  console.log(PageInfo.parse(run.output));
}
