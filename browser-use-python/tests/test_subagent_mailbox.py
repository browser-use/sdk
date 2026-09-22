"""Exercise the reference parent adapter through the real SDK HTTP boundary."""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from uuid import UUID

import httpx
import pytest

from browser_use_sdk.v4 import AsyncBrowserUse
from examples.subagent_mailbox import Brief, Handle, Mailbox, Notice

RUN = "00000000-0000-0000-0000-000000000001"
SESSION = "00000000-0000-0000-0000-000000000002"
NEXT = "00000000-0000-0000-0000-000000000003"
WORKSPACE = "00000000-0000-0000-0000-000000000004"
HANDLE = Handle(run_id=UUID(RUN), session_id=UUID(SESSION), model="gpt-5.6-luna")


def summary(run_id=RUN, status="completed", result=None):
    return {
        "id": run_id, "task": "read a title", "title": None,
        "model": "gpt-5.6-luna", "contextLimit": 200000, "status": status,
        "result": result, "error": None, "sessionId": SESSION,
        "workspaceId": WORKSPACE, "totalInputTokens": 1, "totalOutputTokens": 1,
        "totalCostUsd": "0.01", "createdAt": "2026-09-22T00:00:00Z",
        "updatedAt": "2026-09-22T00:00:00Z",
    }


def session(run_id=RUN, status="completed"):
    return {**summary(run_id, status), "latestRunId": run_id}


def created(run_id=RUN):
    return {**summary(run_id, "queued"), "eventsUrl": f"/runs/{run_id}/events"}


def receipt(status="pending", run_id=RUN):
    return {
        "id": 7, "sessionId": SESSION, "runId": run_id,
        "mode": "interrupt", "status": status, "text": "change the URL",
        "createdAt": "2026-09-22T00:00:00Z",
    }


@asynccontextmanager
async def adapter(responses):
    requests: list[httpx.Request] = []
    pending = list(responses)

    def respond(request):
        requests.append(request)
        assert pending, f"Unexpected request: {request.method} {request.url.path}"
        method, path, body = pending.pop(0)
        assert (request.method, request.url.path) == (method, path)
        return httpx.Response(200, json=body)

    async with AsyncBrowserUse(api_key="test-only", base_url="https://fixture") as client:
        await client._http._client.aclose()
        client._http._client = httpx.AsyncClient(
            base_url="https://fixture", transport=httpx.MockTransport(respond)
        )
        yield Mailbox(client, interval=0.001), requests
    assert not pending, "Not all expected requests were made"


def terminal(run_id=RUN, status="completed", result=None):
    return [
        ("GET", f"/runs/{run_id}/status", {"status": status}),
        ("GET", f"/runs/{run_id}", summary(run_id, status, result)),
    ]


def test_question_reply_and_replay():
    async def scenario():
        question = json.dumps({"kind": "needs_input", "message": "Which URL?"})
        answer = json.dumps({"kind": "completed", "message": "Example Domain",
                             "evidence": ["https://example.com"]})
        responses = [
            ("POST", "/runs", created()),
            *terminal(result=question),
            ("GET", f"/sessions/{SESSION}", session()),
            ("POST", "/runs", created(NEXT)),
            *terminal(NEXT, result=answer),
            *terminal(NEXT, result=answer),
        ]
        async with adapter(responses) as (mailbox, requests):
            inbox: dict[str, Notice] = {}

            async def deliver(notice):
                inbox.setdefault(notice.id, notice)

            handle = await mailbox.start(Brief(
                objective="Read the title", constraints=["Ask for the URL first"],
                permitted_actions=["Read only"], success_criteria=["Report the title"],
                context=["The parent has the URL"],
            ))
            restored = Handle.model_validate_json(handle.model_dump_json())
            notice = await mailbox.watch(restored, deliver)
            assert notice.kind == "needs_input"
            follow_up = await mailbox.reply(notice, "Use https://example.com")
            first = await mailbox.watch(follow_up, deliver)
            replay = await mailbox.watch(follow_up, deliver)
            assert first == replay
            assert first.kind == "completed"
            assert first.message == "Example Domain"
            assert first.evidence == ["https://example.com"]
            assert len(inbox) == 2
            posts = [json.loads(r.content) for r in requests if r.method == "POST"]
            assert "sessionId" not in posts[0]
            assert "Read only" in posts[0]["task"]
            assert posts[0]["maxCostUsd"] == 0.25
            assert posts[1]["sessionId"] == SESSION
            assert posts[1]["model"] == "gpt-5.6-luna"
            assert "https://example.com" in posts[1]["task"]
    asyncio.run(scenario())


def test_callback_failure_is_replayable():
    async def scenario():
        result = '{"kind":"completed","message":"done"}'
        async with adapter(terminal(result=result) * 2) as (mailbox, _):
            attempted = []

            async def fail(notice):
                attempted.append(notice.id)
                raise OSError("parent inbox unavailable")

            with pytest.raises(OSError, match="inbox unavailable"):
                await mailbox.watch(HANDLE, fail)

            async def deliver(notice):
                assert notice.id == attempted[0]

            await mailbox.watch(HANDLE, deliver)
    asyncio.run(scenario())


@pytest.mark.parametrize("result", [
    None, "plain answer", '{"kind":"completed"}',
    '{"kind":"needs_input","message":"  "}',
    '{"kind":"completed","message":"ok","unexpected":true}',
    '{"kind":"completed","message":"ok","evidence":[3]}',
    "x" * 64001,
])
def test_invalid_handoff_is_not_success(result):
    async def scenario():
        async with adapter(terminal(result=result)) as (mailbox, _):
            async def deliver(notice):
                assert notice.kind == "protocol_error"
                assert notice.evidence == []
            await mailbox.watch(HANDLE, deliver)
    asyncio.run(scenario())


def test_steering_waits_for_receipt_and_replacement():
    async def scenario():
        responses = [
            ("GET", f"/sessions/{SESSION}", session(status="running")),
            ("POST", f"/sessions/{SESSION}/queue", receipt()),
            ("GET", f"/sessions/{SESSION}/queue/7", receipt("dispatching")),
            ("GET", f"/sessions/{SESSION}/queue/7", receipt("consumed")),
            ("GET", f"/sessions/{SESSION}", session(status="cancelled")),
            ("GET", f"/sessions/{SESSION}/queue/7", receipt("consumed")),
            ("GET", f"/sessions/{SESSION}", session(NEXT, "running")),
            ("GET", f"/runs/{NEXT}", summary(NEXT, "running")),
            *terminal(NEXT, result='{"kind":"completed","message":"updated result"}'),
        ]
        async with adapter(responses) as (mailbox, requests):
            receipt_id = await mailbox.steer(HANDLE, "Use the new URL")
            assert receipt_id == 7
            replacement = await mailbox.follow_steer(HANDLE, receipt_id)
            assert str(replacement.run_id) == NEXT
            assert replacement.session_id == HANDLE.session_id
            assert json.loads(requests[1].content)["interrupt"] is True

            async def deliver(notice):
                assert notice.message == "updated result"
            await mailbox.watch(replacement, deliver)
    asyncio.run(scenario())


@pytest.mark.parametrize("status", ["superseded", "failed", "cancelled"])
def test_failed_steering_is_not_applied(status):
    async def scenario():
        async with adapter([
            ("GET", f"/sessions/{SESSION}/queue/7", receipt(status)),
        ]) as (mailbox, _):
            with pytest.raises(RuntimeError, match=status):
                await mailbox.follow_steer(HANDLE, 7)
    asyncio.run(scenario())


def test_steering_timeout_does_not_resubmit():
    async def scenario():
        async with adapter([
            ("GET", f"/sessions/{SESSION}/queue/7", receipt()),
        ]) as (mailbox, _):
            with pytest.raises(TimeoutError, match="keep the receipt"):
                await mailbox.follow_steer(HANDLE, 7, timeout=0)
    asyncio.run(scenario())


def test_stale_reply_never_starts_another_run():
    async def scenario():
        async with adapter([
            ("GET", f"/sessions/{SESSION}", session(NEXT)),
        ]) as (mailbox, _):
            notice = Notice(id="question", handle=HANDLE, kind="needs_input", message="URL?")
            with pytest.raises(ValueError, match="stale question"):
                await mailbox.reply(notice, "example.com")
    asyncio.run(scenario())


@pytest.mark.parametrize("status", ["failed", "cancelled"])
def test_run_failure_is_delivered(status):
    async def scenario():
        async with adapter(terminal(status=status)) as (mailbox, _):
            async def deliver(notice):
                assert notice.kind == status
            await mailbox.watch(HANDLE, deliver)
    asyncio.run(scenario())


def test_cancel_targets_only_the_run():
    async def scenario():
        async with adapter([
            ("POST", f"/runs/{RUN}/cancel", summary(status="cancelled")),
        ]) as (mailbox, _):
            await mailbox.cancel(HANDLE)
    asyncio.run(scenario())


def test_foreign_steering_receipt_is_rejected():
    async def scenario():
        async with adapter([
            ("GET", f"/sessions/{SESSION}/queue/7", receipt("consumed", NEXT)),
        ]) as (mailbox, _):
            with pytest.raises(ValueError, match="different source"):
                await mailbox.follow_steer(HANDLE, 7)
    asyncio.run(scenario())
