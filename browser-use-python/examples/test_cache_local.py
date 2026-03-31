"""
Quick local test for the cache & rerun flow.
Tests against localhost:8000 backend.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from browser_use_sdk.v3 import AsyncBrowserUse

API_KEY = "bu_0dsX8mAwNWcOgNkJhx23dQRTtJ49wERSKdvu6RPJK7s"
BASE_URL = "http://localhost:8000/api/v3"


async def main():
    client = AsyncBrowserUse(api_key=API_KEY, base_url=BASE_URL)

    # Create workspace
    print("Creating workspace...")
    ws = await client.workspaces.create(name="cache-rerun-e2e")
    print(f"Workspace: {ws.id}")

    # Step 1: Run with cache=True
    print("\n--- Step 1: Run with cache=True ---")
    print("Running HN scraper task (this will take a minute)...")
    result = await client.run(
        "Go to https://news.ycombinator.com and get the top 5 stories. "
        "Return a JSON array with: title, url, points.",
        workspace_id=str(ws.id),
        cache=True,
    )
    print(f"Status: {result.session.status.value}")
    print(f"Task ID: {result.task_id}")
    print(f"Output: {json.dumps(result.output, indent=2)[:500] if result.output else 'None'}")
    print(f"Cost: ${result.session.total_cost_usd}")

    if not result.task_id:
        print("ERROR: No task_id!")
        await client.close()
        return

    # Check that the script was saved to workspace
    print("\n--- Checking workspace files ---")
    files = await client.workspaces.files(ws.id, prefix=f"tasks/{result.task_id}/")
    print(f"Files in tasks/{result.task_id}/:")
    for f in files.files:
        print(f"  {f.path} ({f.size} bytes)")

    # Step 2: Rerun (no LLM)
    print("\n--- Step 2: Rerun (no LLM) ---")
    rerun = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
    )
    print(f"Status: {rerun.session.status.value}")
    print(f"Output: {json.dumps(rerun.output, indent=2)[:500] if rerun.output else 'None'}")
    print(f"LLM cost: ${rerun.session.llm_cost_usd} (should be $0.00)")

    # Step 3: Rerun again
    print("\n--- Step 3: Second rerun (deterministic) ---")
    rerun2 = await client.rerun(
        task_id=result.task_id,
        workspace_id=str(ws.id),
    )
    print(f"Status: {rerun2.session.status.value}")
    print(f"Output: {json.dumps(rerun2.output, indent=2)[:500] if rerun2.output else 'None'}")

    print("\n--- Done! ---")
    print(f"Workspace ID: {ws.id}")
    print(f"Task ID: {result.task_id}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
