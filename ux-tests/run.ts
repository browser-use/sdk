/**
 * Daily UX test runner — executes all flows and produces a structured report.
 *
 * Usage:
 *   npx tsx run.ts                    # run all flows
 *   npx tsx run.ts --site docs        # run only docs flows
 *   npx tsx run.ts --flow homepage    # run flows matching "homepage"
 */
import { readFileSync, existsSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";

// Load env
const envPaths = [
  resolve(import.meta.dirname, "../.env.prod"),
  resolve(import.meta.dirname, "../.env"),
];
for (const p of envPaths) {
  if (existsSync(p)) {
    for (const line of readFileSync(p, "utf-8").split("\n")) {
      if (!line || line.startsWith("#")) continue;
      const eq = line.indexOf("=");
      if (eq > 0) process.env[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
    }
    break;
  }
}

import { BrowserUse } from "../browser-use-node/src/index.js";
import { flows, UxResult, type UxFlow } from "./flows.js";

const API_KEY = process.env.BROWSER_USE_API_KEY;
if (!API_KEY) {
  console.error("Missing BROWSER_USE_API_KEY in .env.prod or .env");
  process.exit(1);
}

const client = new BrowserUse({ apiKey: API_KEY });

// ── CLI filters ─────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
function getArg(flag: string): string | undefined {
  const i = args.indexOf(flag);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : undefined;
}

const siteFilter = getArg("--site");
const flowFilter = getArg("--flow");

function matchesFilters(flow: UxFlow): boolean {
  if (siteFilter && !flow.site.includes(siteFilter)) return false;
  if (flowFilter && !flow.name.includes(flowFilter)) return false;
  return true;
}

const selectedFlows = flows.filter(matchesFilters);
if (selectedFlows.length === 0) {
  console.error("No flows match the given filters.");
  process.exit(1);
}

// ── Runner ──────────────────────────────────────────────────────────────────

interface FlowResult {
  flow: UxFlow;
  ux: UxResult | null;
  error: string | null;
  durationMs: number;
}

async function runFlow(flow: UxFlow): Promise<FlowResult> {
  const start = Date.now();
  try {
    const prompt = `${flow.task}

After completing the evaluation, provide your assessment as structured output.
Be specific about issues — include what you saw, where on the page, and why it matters.
Only flag real issues, not minor nitpicks. Score fairly: 8+ means good UX with minor issues, 5-7 means notable problems, below 5 means seriously broken.`;

    const result = await client.run(prompt, { schema: UxResult });
    return {
      flow,
      ux: result.output,
      error: null,
      durationMs: Date.now() - start,
    };
  } catch (err) {
    return {
      flow,
      ux: null,
      error: err instanceof Error ? err.message : String(err),
      durationMs: Date.now() - start,
    };
  }
}

// ── Execute ─────────────────────────────────────────────────────────────────

console.log(`\n${"═".repeat(60)}`);
console.log(`  Browser Use — Daily UX Tests`);
console.log(`  ${new Date().toISOString().slice(0, 10)}`);
console.log(`  Running ${selectedFlows.length} flow(s)`);
console.log(`${"═".repeat(60)}\n`);

const results: FlowResult[] = [];

// Run flows sequentially to avoid rate limits
for (const flow of selectedFlows) {
  console.log(`▸ ${flow.name} (${flow.site})`);
  const result = await runFlow(flow);
  results.push(result);

  if (result.ux) {
    const icon = result.ux.passed ? "✓" : "✗";
    console.log(`  ${icon} score=${result.ux.score}/10 load=${result.ux.pageLoadFeeling} (${(result.durationMs / 1000).toFixed(1)}s)`);
    if (result.ux.issues.length > 0) {
      for (const issue of result.ux.issues) {
        console.log(`    ⚠ ${issue}`);
      }
    }
    if (result.ux.suggestions.length > 0) {
      for (const s of result.ux.suggestions) {
        console.log(`    → ${s}`);
      }
    }
  } else {
    console.log(`  ✗ ERROR: ${result.error}`);
  }
  console.log();
}

// ── Summary ─────────────────────────────────────────────────────────────────

const passed = results.filter((r) => r.ux?.passed).length;
const failed = results.filter((r) => !r.ux?.passed).length;
const errors = results.filter((r) => r.error).length;
const avgScore =
  results
    .filter((r) => r.ux)
    .reduce((sum, r) => sum + (r.ux?.score ?? 0), 0) /
  Math.max(results.filter((r) => r.ux).length, 1);

const allIssues = results.flatMap((r) =>
  (r.ux?.issues ?? []).map((issue) => ({ flow: r.flow.name, site: r.flow.site, issue })),
);
const allSuggestions = results.flatMap((r) =>
  (r.ux?.suggestions ?? []).map((s) => ({ flow: r.flow.name, site: r.flow.site, suggestion: s })),
);

console.log(`${"─".repeat(60)}`);
console.log(`Results: ${passed} passed, ${failed} failed, ${errors} errors`);
console.log(`Average UX score: ${avgScore.toFixed(1)}/10`);
console.log();

if (allIssues.length > 0) {
  console.log(`Issues found (${allIssues.length}):`);
  for (const { flow, site, issue } of allIssues) {
    console.log(`  [${site}] ${flow}: ${issue}`);
  }
  console.log();
}

if (allSuggestions.length > 0) {
  console.log(`Suggestions (${allSuggestions.length}):`);
  for (const { flow, site, suggestion } of allSuggestions) {
    console.log(`  [${site}] ${flow}: ${suggestion}`);
  }
  console.log();
}

// ── Write report ────────────────────────────────────────────────────────────

const reportDir = resolve(import.meta.dirname, "reports");
mkdirSync(reportDir, { recursive: true });

const date = new Date().toISOString().slice(0, 10);
const report = {
  date,
  summary: { passed, failed, errors, avgScore: Number(avgScore.toFixed(1)), totalFlows: results.length },
  results: results.map((r) => ({
    name: r.flow.name,
    site: r.flow.site,
    durationMs: r.durationMs,
    ...(r.ux ? { ux: r.ux } : { error: r.error }),
  })),
};

const reportPath = resolve(reportDir, `${date}.json`);
writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`Report saved: ${reportPath}`);

// ── GitHub Actions summary ──────────────────────────────────────────────────

if (process.env.GITHUB_STEP_SUMMARY) {
  const md = [
    `## UX Test Report — ${date}`,
    "",
    `| Metric | Value |`,
    `|--------|-------|`,
    `| Passed | ${passed} |`,
    `| Failed | ${failed} |`,
    `| Errors | ${errors} |`,
    `| Avg Score | ${avgScore.toFixed(1)}/10 |`,
    "",
  ];

  if (allIssues.length > 0) {
    md.push("### Issues", "");
    for (const { flow, site, issue } of allIssues) {
      md.push(`- **${flow}** (${site}): ${issue}`);
    }
    md.push("");
  }

  if (allSuggestions.length > 0) {
    md.push("### Suggestions", "");
    for (const { flow, site, suggestion } of allSuggestions) {
      md.push(`- **${flow}** (${site}): ${suggestion}`);
    }
    md.push("");
  }

  // Per-flow details
  md.push("### Flow Details", "");
  md.push("| Flow | Site | Score | Load | Passed | Duration |");
  md.push("|------|------|-------|------|--------|----------|");
  for (const r of results) {
    if (r.ux) {
      md.push(
        `| ${r.flow.name} | ${r.flow.site} | ${r.ux.score}/10 | ${r.ux.pageLoadFeeling} | ${r.ux.passed ? "✅" : "❌"} | ${(r.durationMs / 1000).toFixed(1)}s |`,
      );
    } else {
      md.push(`| ${r.flow.name} | ${r.flow.site} | — | — | ❌ Error | ${(r.durationMs / 1000).toFixed(1)}s |`);
    }
  }

  writeFileSync(process.env.GITHUB_STEP_SUMMARY, md.join("\n"), { flag: "a" });
}

process.exit(failed > 0 || errors > 0 ? 1 : 0);
