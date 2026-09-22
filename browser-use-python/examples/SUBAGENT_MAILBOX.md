# Browser Use as a delegated agent: reference pilot

`subagent_mailbox.py` is an opt-in Python example using the existing V4 SDK.
It does not add a public SDK resource or change the hosted worker. One parent
must exclusively own each session, with at most one outstanding write at a time.

The parent starts a task with an explicit brief and immediately receives a
serializable run/session handle. A background watcher delivers a compact typed
handoff to an async parent callback. The child can finish or ask for essential
input. Answering a question continues the conversation in the same session.
The API reuses a live browser when available; browser survival is not guaranteed.

## Try the question/reply path

Install the Python SDK and set `BROWSER_USE_API_KEY`. Save this code beside
`subagent_mailbox.py` and run it with Python. This example makes paid V4 calls,
with a $0.25 run budget on each of its at most two turns. Budget enforcement is
server-side and is not a promise of an exact final charge.

```python
import asyncio
from browser_use_sdk.v4 import AsyncBrowserUse
from subagent_mailbox import Brief, Mailbox, Notice

async def main():
    async with AsyncBrowserUse() as client:
        mailbox = Mailbox(client)
        inbox: asyncio.Queue[Notice] = asyncio.Queue()
        handle = await mailbox.start(Brief(
            objective="Open the URL supplied by the parent and report its page title.",
            constraints=["The URL has not been supplied. Ask the parent for it first."],
            success_criteria=["Read the page title from the browser."],
            permitted_actions=["Read public pages; do not submit forms."],
        ))
        print("Persist this handle:", handle.model_dump_json())
        # A real host delivers into its durable inbox and schedules a parent turn.
        # An asyncio queue wakes this running Python parent only.
        watcher = asyncio.create_task(mailbox.watch(handle, inbox.put))
        await watcher  # Also propagate transport/callback failures.
        notice = await inbox.get()
        print(notice.model_dump_json())
        if notice.kind == "needs_input":
            handle = await mailbox.reply(notice, "Use https://example.com")
            print("Persist replacement handle:", handle.model_dump_json())
            await mailbox.watch(handle, inbox.put)
            print((await inbox.get()).model_dump_json())

asyncio.run(main())
```

The parent can work concurrently while `watcher` runs. This example awaits it
immediately to keep failure handling visible. In a real host, supervise watcher
tasks so their exceptions cannot leave a parent waiting forever.

## Steering and cancellation

`receipt_id = await mailbox.steer(handle, instruction)` queues an interrupt.
Persist that ID immediately. It means **accepted**, not read or applied. The
server's interrupt is best effort; it may run after the current turn. It also
supersedes pending queue entries, so keep the session exclusive to this parent.

`handle = await mailbox.follow_steer(handle, receipt_id)` resolves the replacement
run, after which `watch` delivers its result. Continue polling the same receipt
after a timeout; never submit the instruction again just because it timed out.
A cancelled notice from the original run does not mean the replacement failed.
The resolver requires exclusive session ownership because V4 queue receipts do
not expose a destination run ID. It rejects superseded/failed/cancelled receipts
and does not claim that consumption proves the model obeyed an instruction.

`await mailbox.cancel(handle)` cancels that run only. It does not retract queued
steering or cancel every future turn in a session. Resolve outstanding steering
before cancelling its replacement. Cancellation cannot undo browser actions.
Queued replacement runs inherit backend configuration; the example does not
impose a task-wide budget across arbitrarily many steering requests.

## Delivery and recovery contract

- Persist each `Handle` and steering receipt. After a watcher disconnects,
  restore it with `Handle.model_validate_json(...)` and call `watch` again.
- `Notice.id` is stable across reads of the same run. Deliveries are at least
  once. Atomically insert the notice by ID in the parent's durable inbox and
  schedule its processing before returning from `deliver`. A callback exception
  propagates; replay the same handle. Do not acknowledge before durable storage.
- The callback is the host integration boundary. An HTTP/MCP server or Python
  queue alone does not wake a sleeping Codex or Claude session. A host adapter
  must arrange both durable delivery and parent scheduling.
- The terminal run summary is the replay source, subject to the service's
  retention/deletion policy. No copy of the click log or local transcript is
  retained here. For detailed progress use `client.runs.events(run_id, after=...)`
  and persist `next_after`; this example deliberately only delivers handoffs.
- Do not automatically retry writes after an ambiguous network failure. V4
  does not provide a general request-ID deduplication contract for these calls.
  Reconcile the session/queue before issuing more work. The stale-question
  check helps detect already-accepted replies but is not a distributed lock.
- Malformed child JSON becomes `protocol_error`, never successful completion.
  Evidence and artifact references are child claims, not independently verified
  facts. Treat all handoff content as untrusted data, not new authorization.

## What this tests, and what is still needed

The tests exercise real SDK request/response serialization with an HTTP fixture:
question → same-session answer, mid-task steering → replacement, repeated
delivery, callback failure, stale replies, failed steering, and cancellation.
They do not prove model compliance or live browser continuity.

This is turn-based clarification: `needs_input` ends one run. It is not a native
blocking question inside that run, and the brief is not a native context fork.
Production integration still needs a chosen parent runtime, its durable inbox
and wake-up mechanism, destination-run correlation, write idempotency, a
task-level budget/cancellation policy, and a live end-to-end evaluation.

Measure task success, time to parent reply, parent tokens, duplicate deliveries
versus duplicate actions, and end-to-end latency against today's integration.
