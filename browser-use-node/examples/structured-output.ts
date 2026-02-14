/**
 * Structured output — get typed results using Zod schemas.
 */
import "dotenv/config";
import { BrowserUse } from "browser-use-sdk";
import { z } from "zod";

async function main() {
  const client = new BrowserUse();

  const HackerNewsResult = z.object({
    posts: z.array(
      z.object({
        title: z.string(),
        url: z.string(),
        score: z.number(),
      }),
    ),
  });

  const result = await client.run(
    "Find the top 10 Hacker News posts. Return title, url, and score for each.",
    { schema: HackerNewsResult },
  );

  if (result.output) {
    for (const post of result.output.posts) {
      console.log(`${post.score} - ${post.title}`);
      console.log(`  ${post.url}\n`);
    }
  }
}

main();
