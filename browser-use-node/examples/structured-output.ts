/**
 * Structured output — get typed results using Zod schemas.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";
import { z } from "zod";

async function main() {
  const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

  // Define your output schema with Zod
  const HackerNewsResult = z.object({
    posts: z.array(
      z.object({
        title: z.string(),
        url: z.string(),
        score: z.number(),
      }),
    ),
  });

  // Pass the schema — JSON Schema conversion and parsing happen automatically
  const handle = client.run({
    task: "Find the top 10 Hacker News posts. Return title, url, and score for each.",
    schema: HackerNewsResult,
  });

  const result = await handle.complete();

  // result.parsed is fully typed: { posts: { title: string, url: string, score: number }[] } | null
  if (result.parsed) {
    for (const post of result.parsed.posts) {
      console.log(`${post.score} - ${post.title}`);
      console.log(`  ${post.url}\n`);
    }
  }
}

main();
