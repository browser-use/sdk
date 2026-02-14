"""
Production smoke tests -- verify the SDK works against the real API.

Run: uv run python -m pytest tests/test_prod.py -v -s

Uses .env.prod (or .env as fallback) for BROWSER_USE_API_KEY.
Does NOT override base_url -- hits the default prod endpoint.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import BaseModel

# ── Load env ────────────────────────────────────────────────────────────────

_root = Path(__file__).resolve().parent.parent.parent
_prod_env = _root / ".env.prod"
_fallback_env = _root / ".env"
_env_path = _prod_env if _prod_env.exists() else _fallback_env

_env = {}
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        eq = line.index("=")
        _env[line[:eq].strip()] = line[eq + 1 :].strip()

API_KEY = _env.get("BROWSER_USE_API_KEY", "")

pytestmark = [
    pytest.mark.prod,
    pytest.mark.skipif(not API_KEY, reason="No API key"),
]


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    from browser_use_sdk import BrowserUse

    # No base_url override -- hits prod
    with BrowserUse(api_key=API_KEY) as c:
        yield c


# ── 1. Auth / Billing ──────────────────────────────────────────────────────

class TestBilling:
    def test_account(self, client):
        account = client.billing.account()
        assert hasattr(account, "total_credits_balance_usd")
        assert hasattr(account, "rate_limit")
        assert hasattr(account, "project_id")
        assert isinstance(account.rate_limit, int)


# ── 2. Profile CRUD ────────────────────────────────────────────────────────

class TestProfiles:
    def test_crud_lifecycle(self, client):
        # Create
        profile = client.profiles.create(name="SDK Prod Test")
        assert profile.id is not None
        pid = str(profile.id)

        try:
            # Get
            got = client.profiles.get(pid)
            assert str(got.id) == pid

            # Update
            updated = client.profiles.update(pid, name="SDK Prod Updated")
            assert str(updated.id) == pid

            # List
            listing = client.profiles.list(page_size=5)
            assert hasattr(listing, "items")
            assert isinstance(listing.items, list)
        finally:
            # Delete
            client.profiles.delete(pid)


# ── 3. Task lifecycle ──────────────────────────────────────────────────────

class TestTaskLifecycle:
    def test_run_returns_task_result(self, client):
        """run() returns TaskResult with output and metadata."""
        from browser_use_sdk import TaskResult

        result = client.run("Return the exact text: hello world")
        assert isinstance(result, TaskResult)
        assert isinstance(result.output, str)
        assert len(result.output) > 0
        assert result.id is not None
        assert result.status is not None
        assert hasattr(result, "steps")
        assert result.task is not None


# ── 4. Structured output ───────────────────────────────────────────────────

class MathResult(BaseModel):
    answer: int
    explanation: str


class TestStructuredOutput:
    def test_run_with_schema(self, client):
        """run() with schema returns TaskResult with parsed model."""
        from browser_use_sdk import TaskResult

        result = client.run(
            "What is 7 * 8? Return the answer and a one-sentence explanation.",
            schema=MathResult,
        )
        assert isinstance(result, TaskResult)
        assert isinstance(result.output, MathResult)
        assert isinstance(result.output.answer, int)
        assert isinstance(result.output.explanation, str)
        assert len(result.output.explanation) > 0
        assert result.id is not None


# ── 5. Streaming ───────────────────────────────────────────────────────────

class TestStreaming:
    def test_stream_yields_steps(self, client):
        """stream() yields TaskStepView with step-by-step details."""
        from browser_use_sdk import TaskResult

        stream = client.stream("Return the exact text: ping")
        count = 0
        for step in stream:
            assert hasattr(step, "number")
            assert hasattr(step, "next_goal")
            assert hasattr(step, "url")
            count += 1
            if count > 50:
                break  # safety valve
        assert count >= 1

        # result should be a TaskResult after iteration
        assert stream.result is not None
        assert isinstance(stream.result, TaskResult)
        assert stream.result.id is not None


# ── 6. Session lifecycle ───────────────────────────────────────────────────

class TestSessionLifecycle:
    def test_create_stop_delete(self, client):
        session = client.sessions.create()
        sid = str(session.id)
        try:
            assert session.id is not None

            # List
            listing = client.sessions.list(page_size=5)
            assert hasattr(listing, "items")

            # Get
            got = client.sessions.get(sid)
            assert str(got.id) == sid
        finally:
            # Stop + delete
            try:
                client.sessions.stop(sid)
            except Exception:
                pass
            try:
                client.sessions.delete(sid)
            except Exception:
                pass


# ── 7. Error handling ──────────────────────────────────────────────────────

class TestErrors:
    def test_404_on_invalid_task(self, client):
        from browser_use_sdk._core.errors import BrowserUseError

        with pytest.raises(BrowserUseError) as exc_info:
            client.tasks.get("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404

    def test_auth_error_on_invalid_key(self):
        from browser_use_sdk import BrowserUse
        from browser_use_sdk._core.errors import BrowserUseError

        bad = BrowserUse(api_key="bu_invalid_key")
        with pytest.raises(BrowserUseError) as exc_info:
            bad.billing.account()
        assert exc_info.value.status_code in (401, 403, 404)
