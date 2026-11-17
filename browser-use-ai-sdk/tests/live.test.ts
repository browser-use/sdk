// Live check against Browser Use Cloud (spends a few cents). Needs BROWSER_USE_API_KEY.
import { createBrowserUseTools } from "../src/index";

const { tools } = createBrowserUseTools({ model: "bu-ultrafast", timeoutMs: 300_000 });
const out = await tools.browserUseTask.execute!(
  { task: "Open https://example.com and return the page's main heading text only." },
  { toolCallId: "live", messages: [] },
);
console.log(JSON.stringify(out));
if (out.status !== "completed" || !/example domain/i.test(out.result ?? "")) process.exit(1);
