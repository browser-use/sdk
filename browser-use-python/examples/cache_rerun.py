"""
Cache & Rerun — end-to-end example.

Demonstrates the full caching/rerun flow:
1. Run a task with cache=True → agent explores and saves a reusable script
2. Rerun the saved script deterministically without any LLM
3. Rerun with auto-heal (LLM validates output, re-triggers agent if broken)

Usage:
  export BROWSER_USE_API_KEY=bu_...
  # Against local backend:
  export BROWSER_USE_BASE_URL=http://localhost:8000/api/v3
  uv run python examples/cache_rerun.py
"""

import asyncio
import json
import os
import sys

# Allow running from the repo root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from browser_use_sdk.v3 import AsyncBrowserUse, SessionResult


async def test_hackernews():
    """Test 1: Hacker News — simple cache and rerun."""
    print("\n" + "=" * 60)
    print("TEST 1: Hacker News — Cache & Rerun")
    print("=" * 60)

    client = AsyncBrowserUse(
        base_url=os.environ.get("BROWSER_USE_BASE_URL", "https://api.browser-use.com/api/v3"),
    )

    # Step 1: Create a workspace
    print("\n→ Creating workspace...")
    ws = await client.workspaces.create(name="hn-cache-test")
    print(f"  Workspace: {ws.id}")

    # Step 2: Run with cache=True
    print("\n→ Running task with cache=True (agent will explore HN and save script)...")
    result: SessionResult = await client.run(
        "Go to https://news.ycombinator.com and get the top 5 stories. "
        "Return a JSON array with objects having: title, url, points, rank.",
        workspace_id=str(ws.id),
        cache=True,
    )
    print(f"  Status: {result.session.status.value}")
    print(f"  Task ID: {result.task_id}")
    print(f"  Output: {json.dumps(result.output, indent=2)[:500]}")

    if not result.task_id:
        print("  ERROR: No task_id returned!")
        return

    # Step 3: Rerun — no LLM, just executes the saved script
    print("\n→ Rerunning cached script (NO LLM call)...")
    rerun_result = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
    )
    print(f"  Status: {rerun_result.session.status.value}")
    print(f"  Output: {json.dumps(rerun_result.output, indent=2)[:500]}")
    print(f"  Cost: ${rerun_result.session.total_cost_usd}")

    # Verify no LLM cost (script execution should be free of LLM costs)
    print(f"  LLM cost: ${rerun_result.session.llm_cost_usd} (should be $0)")

    # Step 4: Rerun again to verify deterministic behavior
    print("\n→ Rerunning again (should be deterministic)...")
    rerun2 = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
    )
    print(f"  Status: {rerun2.session.status.value}")
    print(f"  Output: {json.dumps(rerun2.output, indent=2)[:500]}")

    # Cleanup
    await client.workspaces.delete(ws.id)
    await client.close()
    print("\n✓ Test 1 complete!")


async def test_intro_marketplace():
    """Test 2: intro.co marketplace — cache with parameters."""
    print("\n" + "=" * 60)
    print("TEST 2: intro.co Marketplace — Cache with Parameters")
    print("=" * 60)

    client = AsyncBrowserUse(
        base_url=os.environ.get("BROWSER_USE_BASE_URL", "https://api.browser-use.com/api/v3"),
    )

    # Step 1: Create workspace
    print("\n→ Creating workspace...")
    ws = await client.workspaces.create(name="intro-cache-test")
    print(f"  Workspace: {ws.id}")

    # Step 2: Run with cache=True — agent explores intro.co and saves parameterized script
    print("\n→ Running task with cache=True (agent explores intro.co/marketplace)...")
    result: SessionResult = await client.run(
        "Go to https://intro.co/marketplace and scrape all expert profiles. "
        "The script should accept a parameter 'keywords' (a list of strings) and "
        "filter experts whose name or title contains any of those keywords. "
        "Return a JSON array of objects with: name, title, profile_url, and any other visible info.",
        workspace_id=str(ws.id),
        cache=True,
    )
    print(f"  Status: {result.session.status.value}")
    print(f"  Task ID: {result.task_id}")
    print(f"  Output preview: {json.dumps(result.output, indent=2)[:500]}")

    if not result.task_id:
        print("  ERROR: No task_id returned!")
        return

    # Step 3: Rerun with parameters — filter for logistics experts
    print("\n→ Rerunning with params: keywords=['logistics'] (NO LLM)...")
    rerun_result = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
        params={"keywords": ["logistics"]},
    )
    print(f"  Status: {rerun_result.session.status.value}")
    print(f"  Output: {json.dumps(rerun_result.output, indent=2)[:500]}")

    # Step 4: Rerun with different parameters — filter for e-commerce
    print("\n→ Rerunning with params: keywords=['e-commerce'] (NO LLM)...")
    rerun2 = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
        params={"keywords": ["e-commerce"]},
    )
    print(f"  Status: {rerun2.session.status.value}")
    print(f"  Output: {json.dumps(rerun2.output, indent=2)[:500]}")

    # Cleanup
    await client.workspaces.delete(ws.id)
    await client.close()
    print("\n✓ Test 2 complete!")


async def test_auto_heal():
    """Test 3: Auto-heal — rerun with auto=True validates output."""
    print("\n" + "=" * 60)
    print("TEST 3: Auto-Heal Flow")
    print("=" * 60)

    client = AsyncBrowserUse(
        base_url=os.environ.get("BROWSER_USE_BASE_URL", "https://api.browser-use.com/api/v3"),
    )

    # Step 1: Create workspace
    print("\n→ Creating workspace...")
    ws = await client.workspaces.create(name="autoheal-test")
    print(f"  Workspace: {ws.id}")

    # Step 2: Run with cache
    print("\n→ Running initial task with cache=True...")
    result = await client.run(
        "Go to https://news.ycombinator.com and get the top 3 stories as JSON "
        "with fields: title, url, points.",
        workspace_id=str(ws.id),
        cache=True,
    )
    print(f"  Task ID: {result.task_id}")

    if not result.task_id:
        print("  ERROR: No task_id returned!")
        return

    # Step 3: Rerun with auto=True (LLM checks output quality)
    print("\n→ Rerunning with auto=True (LLM validates output)...")
    rerun_result = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
        auto=True,
    )
    print(f"  Status: {rerun_result.session.status.value}")
    print(f"  Output: {json.dumps(rerun_result.output, indent=2)[:500]}")

    # Cleanup
    await client.workspaces.delete(ws.id)
    await client.close()
    print("\n✓ Test 3 complete!")


async def main():
    print("Cache & Rerun — End-to-End Tests")
    print("API: " + os.environ.get("BROWSER_USE_BASE_URL", "https://api.browser-use.com/api/v3"))

    test = os.environ.get("TEST", "all")

    if test in ("all", "hn"):
        await test_hackernews()
    if test in ("all", "intro"):
        await test_intro_marketplace()
    if test in ("all", "heal"):
        await test_auto_heal()

    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
