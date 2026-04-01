"""
Script Caching — run a task once, rerun it for $0.

Uses {{double brackets}} to define parameters. The first call runs
the full agent. Subsequent calls with the same template execute
the cached script directly — no LLM, no agent, instant.

Usage:
  export BROWSER_USE_API_KEY=bu_...
  python examples/cache_rerun.py
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from browser_use_sdk.v3 import AsyncBrowserUse


async def main():
    client = AsyncBrowserUse()
    ws = await client.workspaces.create(name="cache-demo")
    ws_id = str(ws.id)
    print(f"Workspace: {ws_id}\n")

    # ── Example 1: Hacker News with parameterized count ──
    print("=" * 60)
    print("Example 1: Hacker News (parameterized)")
    print("=" * 60)

    # First call — agent explores HN, creates script
    print("\n→ First call (agent)...")
    r1 = await client.run(
        "Get the top {{5}} stories from https://news.ycombinator.com as JSON with title, url, points",
        workspace_id=ws_id,
    )
    print(f"  Total cost: ${r1.total_cost_usd}")
    print(f"  Output: {str(r1.output)[:200]}")

    # Second call — cached, $0
    print("\n→ Second call (cached, different param)...")
    r2 = await client.run(
        "Get the top {{3}} stories from https://news.ycombinator.com as JSON with title, url, points",
        workspace_id=ws_id,
    )
    print(f"  LLM cost: ${r2.llm_cost_usd} (should be $0)")
    print(f"  Output: {str(r2.output)[:200]}")

    # ── Example 2: intro.co marketplace with keyword filter ──
    print("\n" + "=" * 60)
    print("Example 2: intro.co marketplace (parameterized keyword)")
    print("=" * 60)

    print("\n→ First call (agent)...")
    r3 = await client.run(
        "Go to {{https://intro.co/marketplace}} and get all {{logistics}} experts as JSON",
        workspace_id=ws_id,
    )
    print(f"  Total cost: ${r3.total_cost_usd}")

    for keyword in ["CEO", "marketing", "finance"]:
        print(f"\n→ Cached rerun: keyword={keyword}...")
        r = await client.run(
            f"Go to {{{{https://intro.co/marketplace}}}} and get all {{{{{keyword}}}}} experts as JSON",
            workspace_id=ws_id,
        )
        data = r.output if isinstance(r.output, list) else []
        print(f"  LLM cost: ${r.llm_cost_usd} | Found: {len(data)} experts")

    # ── Example 3: No parameters — cache exact task ──
    print("\n" + "=" * 60)
    print("Example 3: No parameters (empty brackets)")
    print("=" * 60)

    print("\n→ First call (agent)...")
    r5 = await client.run(
        "Get the current top mass shooting statistics from Wikipedia {{}}",
        workspace_id=ws_id,
    )
    print(f"  Total cost: ${r5.total_cost_usd}")

    print("\n→ Cached rerun...")
    r6 = await client.run(
        "Get the current top mass shooting statistics from Wikipedia {{}}",
        workspace_id=ws_id,
    )
    print(f"  LLM cost: ${r6.llm_cost_usd} (should be $0)")

    await client.workspaces.delete(ws.id)
    await client.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
