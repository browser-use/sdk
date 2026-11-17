# browser-use-ai-sdk

[Browser Use](https://browser-use.com) tools for the [Vercel AI SDK](https://ai-sdk.dev). Your model hands a web task to a Browser Use agent running in a stealth cloud browser (proxies, CAPTCHA handling) and gets the answer back.

```bash
npm install browser-use-ai-sdk ai zod
export BROWSER_USE_API_KEY=bu_...   # https://cloud.browser-use.com/settings?tab=api-keys&new=1
```

```ts
import { generateText, isStepCount } from "ai";
import { createBrowserUseTools } from "browser-use-ai-sdk";

const browserUse = createBrowserUseTools();

const { text } = await generateText({
  model: "anthropic/claude-sonnet-5.5",
  tools: browserUse.tools,
  stopWhen: isStepCount(5),
  prompt: "Open https://news.ycombinator.com and summarize the top 3 stories.",
});

console.log(text);
```

## Tool

`browserUseTask({ task, sessionId? })` creates one run on the Browser Use Cloud v4 API, waits for it to finish and returns `{ status, result, error, sessionId, costUsd }`. Pass the returned `sessionId` to continue in the same browser.

## Options

`createBrowserUseTools({ apiKey, model, timeoutMs, client })`

- `apiKey`: defaults to `BROWSER_USE_API_KEY`.
- `model`: Browser Use agent model, e.g. `bu-4.0` or `bu-ultrafast`. Omit to use the project default.
- `timeoutMs`: max wait per task. Default 10 minutes.
- `client`: an existing `BrowserUse` client from `browser-use-sdk/v4`.

Pricing: https://browser-use.com/pricing. Docs: https://docs.browser-use.com.
