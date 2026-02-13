/**
 * Structured output — get typed results using Zod schemas.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";
import { z } from "zod";

async function main() {
  const client = new BrowserUse();

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
  const parsed = await client.run(
    "Find the top 10 Hacker News posts. Return title, url, and score for each.",
    { schema: HackerNewsResult },
  );

  // parsed is fully typed: { posts: { title: string, url: string, score: number }[] }
  if (parsed) {
    for (const post of parsed.posts) {
      console.log(`${post.score} - ${post.title}`);
      console.log(`  ${post.url}\n`);
    }
  }
}

main();
