"""Local HTTP evidence for bounded initial visibility recovery.

HTTP is real loopback; budget tests replace only clock/sleep functions. The server deliberately schedules a visibility lag;
this does not emulate PostgreSQL or establish the customer's SDK version.
"""
import asyncio
import json
import threading
import time
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from browser_use_sdk._core.errors import BrowserUseError
from browser_use_sdk.v4.client import AsyncBrowserUse, BrowserUse
from browser_use_sdk.v4.resources import runs as runs_module

RUN = "00000000-0000-0000-0000-000000000001"
SESSION = "00000000-0000-0000-0000-000000000002"
WORKSPACE = "00000000-0000-0000-0000-000000000003"


def summary(status):
    return dict(id=RUN, task="local fixture", title=None, model="fixture-model",
                contextLimit=1000, status=status, result="done" if status == "completed" else None,
                error=None, sessionId=SESSION, workspaceId=WORKSPACE,
                totalInputTokens=0, totalOutputTokens=0, totalCostUsd="0",
                createdAt="2026-09-21T00:00:00Z", updatedAt="2026-09-21T00:00:00Z")


@contextmanager
def fixture_http(plan, complete_after: float | None = 0.03, status_delay: float = 0):
    class State:
        def __init__(self):
            self.calls = []
            self.plan = list(plan)
            self.completed = threading.Event()
            self.polled = threading.Event()
            self.cancelled = False
            self.timer: threading.Timer | None = None
            self.url = ""
    state = State()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, code, body):
            raw = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
            state.calls.append(("POST", self.path))
            if self.path == "/api/v4/runs":
                assert body["task"] == "local fixture"
                assert body["model"] == "fixture-model"
                if complete_after is not None:
                    state.timer = threading.Timer(complete_after, state.completed.set)
                    state.timer.start()
                self.reply(201, dict(id=RUN, status="queued", model="fixture-model",
                                    sessionId=SESSION, workspaceId=WORKSPACE, eventsUrl=f"/runs/{RUN}/events"))
            elif self.path == f"/api/v4/runs/{RUN}/cancel":
                state.cancelled = True
                self.reply(200, summary("cancelled"))
            else:
                self.reply(404, {"detail": "unknown fixture route"})

        def do_GET(self):
            state.calls.append(("GET", self.path))
            if self.path == f"/api/v4/runs/{RUN}/status":
                state.polled.set()
                value = state.plan.pop(0) if len(state.plan) > 1 else state.plan[0]
                if status_delay:
                    time.sleep(status_delay)
                if isinstance(value, int):
                    self.reply(value, {"detail": "fixture HTTP error"})
                else:
                    if value == "completed":
                        assert state.completed.wait(0.5)
                    self.reply(200, {"status": value})
            elif self.path == f"/api/v4/runs/{RUN}":
                self.reply(200, summary("cancelled" if state.cancelled else "completed" if state.completed.is_set() else "running"))
            else:
                self.reply(404, {"detail": "unknown fixture route"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.005), daemon=True)
    thread.start()
    state.url = f"http://127.0.0.1:{server.server_port}/api/v4"
    try:
        yield state
    finally:
        if state.timer:
            state.timer.cancel()
            state.timer.join()
        server.shutdown()
        server.server_close()
        thread.join()


def client(state):
    return AsyncBrowserUse(api_key="local-fixture-not-a-secret", base_url=state.url, timeout=0.5)


async def create(c):
    return await c.runs.create("local fixture", model="fixture-model", model_params={})


def count(state, suffix, method="GET"):
    return sum(m == method and p.endswith(suffix) for m, p in state.calls)


def observe(name, state, **data):
    print("OBSERVATION " + json.dumps(dict(name=name, calls=state.calls, **data)), flush=True)


def test_proposed_initial_visibility_recovery_red():
    """PROPOSED: bounded initial 404 recovery after acknowledged create, not an existing SDK promise."""
    async def run():
        with fixture_http([404, "running", "completed"]) as s:
            async with client(s) as c:
                created = await create(c)
                start = time.monotonic()
                result = None
                failure = None
                try:
                    result = await asyncio.wait_for(c.runs.wait_for_completion(created.id, timeout=0.25, interval=0.005), timeout=0.35)
                except Exception as exc:
                    failure = exc
                elapsed = time.monotonic() - start
                waiter_polls = count(s, "/status")
                assert await asyncio.to_thread(s.completed.wait, 0.5)
                completed = await c.runs.get(created.id)  # Diagnostic read after waiter outcome.
                assert completed.status.value == "completed"
                assert count(s, "/runs", "POST") == 1
                assert not s.cancelled
                observe("proposed_visibility", s, elapsed_s=elapsed, waiter_polls=waiter_polls,
                        failure_type=type(failure).__name__ if failure else None,
                        failure_status=getattr(failure, "status_code", None), fixture_completed=True)
                assert result is not None and result.status.value == "completed", (
                    f"Proposed initial-visibility recovery failed: {type(failure).__name__}: {failure}; "
                    f"waiter made {waiter_polls} status GET(s), fixture completed independently"
                )
                assert elapsed < 0.35
                assert 3 <= waiter_polls <= 6
    asyncio.run(run())


def test_normal_create_wait_control():
    async def run():
        with fixture_http(["running", "completed"]) as s:
            async with client(s) as c:
                created = await create(c)
                start = time.monotonic()
                result = await asyncio.wait_for(c.runs.wait_for_completion(created.id, timeout=0.25, interval=0.005), 0.35)
                elapsed = time.monotonic() - start
                assert result.status.value == "completed"
                assert count(s, "/status") == 2
                assert count(s, f"/runs/{RUN}") == 1
                assert count(s, "/runs", "POST") == 1
                observe("normal", s, elapsed_s=elapsed)
    asyncio.run(run())


@pytest.mark.parametrize("code", [404, 401, 403])
def test_permanent_missing_and_auth_error_controls(code):
    async def run():
        with fixture_http([code], complete_after=None) as s:
            async with client(s) as c:
                # Permanent404 uses an ID never created; auth controls follow a successful create.
                run_id = "00000000-0000-0000-0000-000000000099" if code == 404 else (await create(c)).id
                with pytest.raises(BrowserUseError) as caught:
                    await asyncio.wait_for(c.runs.wait_for_completion(run_id, timeout=0.1, interval=0.005), 0.2)
                assert caught.value.status_code == code
                assert 1 <= count(s, "/status") <= 3 if code == 404 else count(s, "/status") == 1
                assert count(s, "/runs", "POST") == (0 if code == 404 else 1)
                assert not s.cancelled
                observe(f"permanent_{code}", s)
    asyncio.run(run())


def test_customer_create_wait_recovers_without_timeout_cancellation():
    async def run():
        with fixture_http([404, "running", "completed"]) as s:
            async with client(s) as c:
                task = "local fixture"
                model = "fixture-model"
                model_params = {}
                task_timeout = 0.2
                timeout_handler = False
                run = await c.runs.create(task, model=model, model_params=model_params)
                try:
                    # Same customer flow; only polling cadence is shortened for this fixture.
                    result = await c.runs.wait_for_completion(run.id, timeout=task_timeout, interval=0.005)
                except TimeoutError:
                    timeout_handler = True
                    await c.runs.cancel(run.id)
                    raise
                assert result.status.value == "completed"
                assert not timeout_handler
                assert not s.cancelled
                assert count(s, "/status") == 3
                assert count(s, "/runs", "POST") == 1
                observe("customer_snippet_recovery", s, timeout_handler=False, fixture_completed=True)
    asyncio.run(run())


def test_nonterminal_timeout_and_explicit_cancel_control():
    async def run():
        with fixture_http(["running"], complete_after=None) as s:
            async with client(s) as c:
                created = await create(c)
                with pytest.raises(TimeoutError, match="did not complete"):
                    try:
                        await asyncio.wait_for(c.runs.wait_for_completion(created.id, timeout=0.025, interval=0.005), 0.2)
                    except TimeoutError:
                        assert not s.cancelled  # Waiting alone did not send cancellation.
                        await c.runs.cancel(created.id)
                        raise
                assert s.cancelled
                assert count(s, "/cancel", "POST") == 1
                assert count(s, "/runs", "POST") == 1
                observe("nonterminal_timeout_manual_cancel", s)
    asyncio.run(run())


def test_terminal_status_after_wait_deadline_is_returned_control():
    async def run():
        with fixture_http(["completed"], status_delay=0.04) as s:
            async with client(s) as c:
                created = await create(c)
                start = time.monotonic()
                result = await asyncio.wait_for(c.runs.wait_for_completion(created.id, timeout=0.005), 0.2)
                elapsed = time.monotonic() - start
                assert result.status.value == "completed"
                assert elapsed >= 0.04  # Current documented terminal-result exception to wait deadline.
                observe("terminal_after_deadline", s, elapsed_s=elapsed)
    asyncio.run(run())


def test_caller_cancellation_does_not_cancel_remote_run_control():
    async def run():
        with fixture_http(["running"]) as s:
            async with client(s) as c:
                created = await create(c)
                waiter = asyncio.create_task(c.runs.wait_for_completion(created.id, timeout=1, interval=0.1))
                assert await asyncio.to_thread(s.polled.wait, 0.5)
                waiter.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await waiter
                assert not s.cancelled
                assert await asyncio.to_thread(s.completed.wait, 0.5)
                assert (await c.runs.get(created.id)).status.value == "completed"
                observe("caller_cancellation", s, fixture_completed=True)
    asyncio.run(run())


def test_async_404_after_visible_is_not_retried():
    async def run():
        with fixture_http(["running", 404, "completed"]) as s:
            async with client(s) as c:
                created = await create(c)
                with pytest.raises(BrowserUseError) as caught:
                    await c.runs.wait_for_completion(created.id, timeout=0.2, interval=0.005)
                assert caught.value.status_code == 404
                assert count(s, "/status") == 2
                observe("async_404_after_visible", s)
    asyncio.run(run())


@pytest.mark.parametrize("code", [500, 503])
def test_async_other_http_errors_are_not_retried(code):
    async def run():
        with fixture_http([code], complete_after=None) as s:
            async with client(s) as c:
                created = await create(c)
                with pytest.raises(BrowserUseError) as caught:
                    await c.runs.wait_for_completion(created.id, timeout=0.2, interval=0.005)
                assert caught.value.status_code == code
                assert count(s, "/status") == 1
    asyncio.run(run())


@pytest.mark.parametrize("plan,expected,polls", [
    ([404, "running", "completed"], "completed", 3),
    (["completed"], "completed", 1),
    ([401], 401, 1),
    ([403], 403, 1),
    ([503], 503, 1),
    (["running", 404, "completed"], 404, 2),
])
def test_sync_visibility_and_error_controls(plan, expected, polls):
    with fixture_http(plan) as s:
        with BrowserUse(api_key="local-fixture-not-a-secret", base_url=s.url, timeout=0.5) as c:
            created = c.runs.create("local fixture", model="fixture-model", model_params={})
            if isinstance(expected, int):
                with pytest.raises(BrowserUseError) as caught:
                    c.runs.wait_for_completion(created.id, timeout=0.2, interval=0.005)
                assert caught.value.status_code == expected
            else:
                result = c.runs.wait_for_completion(created.id, timeout=0.2, interval=0.005)
                assert result.status.value == expected
            assert count(s, "/status") == polls
            assert count(s, "/runs", "POST") == 1
            observe("sync_" + str(plan), s)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("timeout,interval,elapsed,polls", [(100, 2, 5, 3), (0.12, 2, 0.12, 1), (0.12, 0, 0.12, 3)])
def test_visibility_budget_uses_original_deadline(mode, timeout, interval, elapsed, polls):
    # Only time/cadence is virtualized: every request still uses actual SDK HTTP/TCP.
    clock = [0.0]
    sleeps = []
    def advance(delay):
        assert delay > 0
        sleeps.append(delay)
        clock[0] += delay
    async def async_advance(delay):
        advance(delay)
    fake_time = SimpleNamespace(monotonic=lambda: clock[0], sleep=advance)
    with fixture_http([404], complete_after=None) as s:
        if mode == "sync":
            with BrowserUse(api_key="local-fixture-not-a-secret", base_url=s.url) as c:
                with patch.object(runs_module, "time", fake_time), pytest.raises(BrowserUseError) as caught:
                    c.runs.wait_for_completion(RUN, timeout=timeout, interval=interval)
                assert caught.value.status_code == 404
        else:
            async def run():
                async with client(s) as c:
                    with patch.object(runs_module, "time", fake_time), patch.object(runs_module, "asyncio", SimpleNamespace(sleep=async_advance)):
                        with pytest.raises(BrowserUseError) as caught:
                            await c.runs.wait_for_completion(RUN, timeout=timeout, interval=interval)
                        assert caught.value.status_code == 404
            asyncio.run(run())
        assert clock[0] == pytest.approx(elapsed)
        assert count(s, "/status") == polls
        assert count(s, "/runs", "POST") == 0
        observe(f"{mode}_budget", s, virtual_elapsed_s=clock[0], timeout=timeout, interval=interval, sleeps=sleeps)


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_healthy_terminal_never_adds_visibility_sleep(mode):
    def forbidden_sleep(_):
        pytest.fail("Healthy terminal path must not add a visibility sleep")
    async def forbidden_async_sleep(_):
        forbidden_sleep(_)
    with fixture_http(["completed"], complete_after=0) as s:
        if mode == "sync":
            with BrowserUse(api_key="local-fixture-not-a-secret", base_url=s.url) as c:
                created = c.runs.create("local fixture", model="fixture-model")
                with patch.object(runs_module, "time", SimpleNamespace(monotonic=time.monotonic, sleep=forbidden_sleep)):
                    assert c.runs.wait_for_completion(created.id).status.value == "completed"
        else:
            async def run():
                async with client(s) as c:
                    created = await create(c)
                    with patch.object(runs_module, "asyncio", SimpleNamespace(sleep=forbidden_async_sleep)):
                        assert (await c.runs.wait_for_completion(created.id)).status.value == "completed"
            asyncio.run(run())
        assert count(s, "/status") == 1
        assert count(s, "/runs", "POST") == 1


def test_async_cancellation_during_visibility_grace_propagates():
    async def run():
        with fixture_http([404]) as s:
            async with client(s) as c:
                created = await create(c)
                sleeping = asyncio.Event()
                async def interrupted_sleep(_):
                    sleeping.set()
                    await asyncio.Future()
                with patch.object(runs_module, "asyncio", SimpleNamespace(sleep=interrupted_sleep)):
                    waiter = asyncio.create_task(c.runs.wait_for_completion(created.id))
                    await asyncio.wait_for(sleeping.wait(), 0.5)
                    waiter.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await waiter
                assert count(s, "/status") == 1
                assert not s.cancelled
    asyncio.run(run())


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_visibility_recovery_does_not_reset_overall_timeout(mode):
    clock = [0.0]
    def advance(delay):
        clock[0] += delay
    async def async_advance(delay):
        advance(delay)
    fake_time = SimpleNamespace(monotonic=lambda: clock[0], sleep=advance)
    with fixture_http([404, "running"], complete_after=None) as s:
        if mode == "sync":
            with BrowserUse(api_key="local-fixture-not-a-secret", base_url=s.url) as c:
                with patch.object(runs_module, "time", fake_time), pytest.raises(TimeoutError):
                    c.runs.wait_for_completion(RUN, timeout=0.12, interval=0.05)
        else:
            async def run():
                async with client(s) as c:
                    with patch.object(runs_module, "time", fake_time), patch.object(runs_module, "asyncio", SimpleNamespace(sleep=async_advance)):
                        with pytest.raises(TimeoutError):
                            await c.runs.wait_for_completion(RUN, timeout=0.12, interval=0.05)
            asyncio.run(run())
        assert clock[0] == pytest.approx(0.12)
        assert count(s, "/status") == 4
        assert not s.cancelled
