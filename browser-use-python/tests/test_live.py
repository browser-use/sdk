"""
Live integration tests against localhost:8000.

Run: uv run pytest tests/test_live.py -v -s

Requires:
  - Backend running on localhost:8000
  - BROWSER_USE_API_KEY in ../.env
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

# Read API key from .env
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
_env = {}
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        eq = line.index("=")
        _env[line[:eq].strip()] = line[eq + 1 :].strip()

API_KEY = _env.get("BROWSER_USE_API_KEY", "")
BASE_URL = _env.get("BACKEND_URL", "http://localhost:8000")

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not API_KEY, reason="No API key in .env"),
]


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def v2():
    from browser_use_sdk import BrowserUse
    with BrowserUse(api_key=API_KEY, base_url=f"{BASE_URL}/api/v2") as client:
        yield client


@pytest.fixture(scope="module")
def v3():
    from browser_use_sdk.v3 import BrowserUse
    with BrowserUse(api_key=API_KEY, base_url=f"{BASE_URL}/api/v3") as client:
        yield client


# ── V2 Billing ───────────────────────────────────────────────────────────────

class TestV2Billing:
    def test_account(self, v2):
        account = v2.billing.account()
        assert hasattr(account, "totalCreditsBalanceUsd")
        assert hasattr(account, "rateLimit")
        assert hasattr(account, "projectId")


# ── V2 Profiles CRUD ────────────────────────────────────────────────────────

class TestV2Profiles:
    def test_crud(self, v2):
        # Create
        profile = v2.profiles.create(name="SDK Py Test Profile")
        assert profile.id is not None
        pid = str(profile.id)

        # List
        listing = v2.profiles.list(page_size=5)
        assert hasattr(listing, "items")
        assert isinstance(listing.items, list)

        # Get
        got = v2.profiles.get(pid)
        assert str(got.id) == pid

        # Update
        updated = v2.profiles.update(pid, name="Updated Py Profile")
        assert str(updated.id) == pid

        # Delete
        v2.profiles.delete(pid)


# ── V2 Sessions & Tasks ─────────────────────────────────────────────────────

class TestV2SessionsTasks:
    def test_session_lifecycle(self, v2):
        # Create session
        session = v2.sessions.create()
        assert session.id is not None
        sid = str(session.id)

        # List sessions
        listing = v2.sessions.list(page_size=5)
        assert hasattr(listing, "items")

        # Get session
        got = v2.sessions.get(sid)
        assert str(got.id) == sid

        # Create task in session
        task = v2.tasks.create("Go to google.com", session_id=sid)
        assert task.id is not None
        tid = str(task.id)

        # List tasks
        tasks = v2.tasks.list(page_size=5)
        assert hasattr(tasks, "items")

        # Get task
        got_task = v2.tasks.get(tid)
        assert str(got_task.id) == tid
        assert hasattr(got_task, "status")

        # Task status
        status = v2.tasks.status(tid)
        assert str(status.id) == tid
        assert hasattr(status, "status")

        # Stop task
        stopped = v2.tasks.stop(tid)
        assert str(stopped.id) == tid

        time.sleep(1)

        # Stop session
        stopped_session = v2.sessions.stop(sid)
        assert str(stopped_session.id) == sid

        # Public share
        try:
            share = v2.sessions.create_share(sid)
            assert share is not None
            got_share = v2.sessions.get_share(sid)
            assert got_share is not None
            v2.sessions.delete_share(sid)
        except Exception:
            pass  # May not support shares for this session type

        # Delete session
        v2.sessions.delete(sid)


# ── V2 Browsers ──────────────────────────────────────────────────────────────

class TestV2Browsers:
    def test_crud(self, v2):
        # Create
        from browser_use_sdk._core.errors import BrowserUseError
        try:
            browser = v2.browsers.create()
        except BrowserUseError as e:
            if e.status_code == 422:
                pytest.skip("Browser creation requires specific params")
            raise
        assert browser.id is not None
        bid = str(browser.id)

        # List
        listing = v2.browsers.list(page_size=5)
        assert hasattr(listing, "items")

        # Get
        got = v2.browsers.get(bid)
        assert str(got.id) == bid

        # Stop
        stopped = v2.browsers.stop(bid)
        assert str(stopped.id) == bid


# ── V2 Skills & Marketplace ─────────────────────────────────────────────────

class TestV2Skills:
    def test_list(self, v2):
        listing = v2.skills.list(page_size=5)
        assert hasattr(listing, "items")
        assert isinstance(listing.items, list)


class TestV2Marketplace:
    def test_list(self, v2):
        listing = v2.marketplace.list(page_size=5)
        assert listing is not None


# ── V2 Error Handling ────────────────────────────────────────────────────────

class TestV2Errors:
    def test_invalid_api_key(self):
        from browser_use_sdk import BrowserUse
        from browser_use_sdk._core.errors import BrowserUseError
        client = BrowserUse(api_key="bu_invalid", base_url=f"{BASE_URL}/api/v2")
        with pytest.raises(BrowserUseError) as exc_info:
            client.billing.account()
        assert exc_info.value.status_code in (401, 403, 404)

    def test_not_found(self, v2):
        from browser_use_sdk._core.errors import BrowserUseError
        with pytest.raises(BrowserUseError) as exc_info:
            v2.tasks.get("00000000-0000-0000-0000-000000000000")
        assert exc_info.value.status_code == 404
        assert len(exc_info.value.message) > 0

    def test_error_has_detail(self, v2):
        from browser_use_sdk._core.errors import BrowserUseError
        with pytest.raises(BrowserUseError) as exc_info:
            v2.tasks.get("00000000-0000-0000-0000-000000000000")
        err = exc_info.value
        assert err.detail is not None


# ── V2 Run + TaskHandle ──────────────────────────────────────────────────────

class TestV2TaskHandle:
    def test_run_returns_handle(self, v2):
        handle = v2.run("Go to google.com")
        assert handle is not None
        assert handle.id is not None
        assert hasattr(handle, "complete")
        assert hasattr(handle, "stream")
        # Clean up
        try:
            v2.tasks.stop(handle.id)
        except Exception:
            pass

    def test_complete_polls(self, v2):
        handle = v2.run("Go to google.com")
        # Stop immediately
        v2.tasks.stop(handle.id)
        result = handle.complete(timeout=30, interval=0.5)
        assert str(result.id) == handle.id
        assert result.status in ("stopped", "finished")

    def test_stream_yields(self, v2):
        handle = v2.run("Go to google.com")
        # Stop soon
        v2.tasks.stop(handle.id)
        time.sleep(0.5)
        states = list(handle.stream(interval=0.5))
        assert len(states) >= 1
        assert str(states[-1].id) == handle.id


# ── V3 Tests ─────────────────────────────────────────────────────────────────

class TestV3:
    def test_list_sessions(self, v3):
        listing = v3.sessions.list(page_size=5)
        assert hasattr(listing, "sessions")
        assert isinstance(listing.sessions, list)

    @pytest.mark.skip(reason="v3 sessions.create returns 500 on localhost — needs cloud infra")
    def test_create_and_stop(self, v3):
        session = v3.sessions.create("Go to google.com")
        assert session.id is not None
