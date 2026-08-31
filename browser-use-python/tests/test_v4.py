"""Mocked-HTTP tests for the v4 namespace (runs polling, sessions queue, pagination)."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest

import browser_use_sdk.v4.resources.workspaces as workspaces_module
from browser_use_sdk.v4 import InlineSecretSource, SecretBinding
from browser_use_sdk.v4.resources.browsers import AsyncBrowsers, Browsers
from browser_use_sdk.v4.resources.runs import AsyncRuns, Runs
from browser_use_sdk.v4.resources.sessions import Sessions
from browser_use_sdk.v4.resources.workspaces import AsyncWorkspaces, Workspaces

RUN_ID = "00000000-0000-0000-0000-000000000001"
SESSION_ID = "00000000-0000-0000-0000-000000000002"
WORKSPACE_ID = "00000000-0000-0000-0000-000000000010"
UPLOAD_ID = "00000000-0000-0000-0000-000000000099"


def _run_summary(status: str) -> dict[str, Any]:
    return {
        "id": RUN_ID,
        "task": "Find pricing",
        "title": None,
        "model": "minimax-m3",
        "contextLimit": 200000,
        "status": status,
        "result": "done" if status == "completed" else None,
        "error": None,
        "sessionId": SESSION_ID,
        "workspaceId": None,
        "totalInputTokens": 1,
        "totalOutputTokens": 1,
        "totalCostUsd": "0.01",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }


def _queued_message(status: str = "pending") -> dict[str, Any]:
    return {
        "id": 7,
        "sessionId": SESSION_ID,
        "runId": None,
        "mode": "queue",
        "status": status,
        "text": "also check the careers page",
        "createdAt": "2026-01-01T00:00:00Z",
    }


def _stopped_browser() -> dict[str, Any]:
    return {
        "id": SESSION_ID,
        "status": "stopped",
        "timeoutAt": "2026-01-01T01:00:00Z",
        "startedAt": "2026-01-01T00:00:00Z",
        "proxyUsedMb": "0",
        "proxyCost": "0",
        "browserCost": "0.01",
        "metadata": {},
    }


class FakeSyncHttp:
    """Fake SyncHttpClient — returns queued responses, records every call."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, json, params))
        return self.responses.pop(0)


class FakeAsyncHttp:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]] = []

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, json, params))
        return self.responses.pop(0)


def test_browsers_stop() -> None:
    http = FakeSyncHttp([_stopped_browser()])
    browsers = Browsers(http)  # type: ignore[arg-type]

    browser = browsers.stop(SESSION_ID)

    assert http.calls[0][:3] == (
        "PATCH",
        f"/browsers/{SESSION_ID}",
        {"action": "stop"},
    )
    assert browser.status.value == "stopped"


def test_async_browsers_stop() -> None:
    async def run() -> None:
        http = FakeAsyncHttp([_stopped_browser()])
        browsers = AsyncBrowsers(http)  # type: ignore[arg-type]

        browser = await browsers.stop(SESSION_ID)

        assert http.calls[0][:3] == (
            "PATCH",
            f"/browsers/{SESSION_ID}",
            {"action": "stop"},
        )
        assert browser.status.value == "stopped"

    asyncio.run(run())


# ---------------------------------------------------------------------------
# runs.wait_for_completion
# ---------------------------------------------------------------------------


def test_wait_for_completion_polls_status_then_fetches_run_once() -> None:
    http = FakeSyncHttp(
        [
            {"status": "queued"},
            {"status": "running"},
            {"status": "completed"},
            _run_summary("completed"),
        ]
    )
    runs = Runs(http)  # type: ignore[arg-type]

    run = runs.wait_for_completion(RUN_ID, interval=0)

    paths = [c[1] for c in http.calls]
    assert paths == [
        f"/runs/{RUN_ID}/status",
        f"/runs/{RUN_ID}/status",
        f"/runs/{RUN_ID}/status",
        f"/runs/{RUN_ID}",
    ]
    assert run.status.value == "completed"
    assert run.result == "done"


def test_wait_for_completion_stops_on_failed() -> None:
    http = FakeSyncHttp([{"status": "failed"}, _run_summary("failed")])
    runs = Runs(http)  # type: ignore[arg-type]

    run = runs.wait_for_completion(RUN_ID, interval=0)

    assert run.status.value == "failed"


def test_wait_for_completion_times_out() -> None:
    http = FakeSyncHttp([{"status": "running"}] * 100)
    runs = Runs(http)  # type: ignore[arg-type]

    with pytest.raises(TimeoutError, match="did not complete"):
        runs.wait_for_completion(RUN_ID, timeout=0.01, interval=0.005)


def test_async_wait_for_completion() -> None:
    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {"status": "running"},
                {"status": "cancelled"},
                _run_summary("cancelled"),
            ]
        )
        runs = AsyncRuns(http)  # type: ignore[arg-type]

        result = await runs.wait_for_completion(RUN_ID, interval=0)

        assert result.status.value == "cancelled"
        assert [c[1] for c in http.calls] == [
            f"/runs/{RUN_ID}/status",
            f"/runs/{RUN_ID}/status",
            f"/runs/{RUN_ID}",
        ]

    asyncio.run(run())


def test_wait_for_event_returns_browser_ready_before_terminal_wait() -> None:
    http = FakeSyncHttp(
        [
            {
                "events": [
                    {
                        "runId": RUN_ID,
                        "id": 1,
                        "ts": "2026-01-01T00:00:00Z",
                        "type": "run.created",
                        "data": {},
                    }
                ],
                "nextAfter": 1,
                "hasMore": True,
            },
            {
                "events": [
                    {
                        "runId": RUN_ID,
                        "id": 2,
                        "ts": "2026-01-01T00:00:01Z",
                        "type": "browser.ready",
                        "data": {"live_view_url": "https://live"},
                    }
                ],
                "nextAfter": 2,
                "hasMore": False,
            },
        ]
    )
    event = Runs(http).wait_for_event(RUN_ID, "browser.ready", interval=0)  # type: ignore[arg-type]
    assert event.data["live_view_url"] == "https://live"
    assert http.calls[-1][3] == {"after": 1, "limit": 100}


def test_async_wait_for_event_returns_browser_ready() -> None:
    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {
                    "events": [],
                    "nextAfter": 0,
                    "hasMore": False,
                },
                {
                    "events": [
                        {
                            "runId": RUN_ID,
                            "id": 1,
                            "ts": "2026-01-01T00:00:01Z",
                            "type": "browser.ready",
                            "data": {"live_view_url": "https://live"},
                        }
                    ],
                    "nextAfter": 1,
                    "hasMore": False,
                },
            ]
        )
        event = await AsyncRuns(http).wait_for_event(  # type: ignore[arg-type]
            RUN_ID, "browser.ready", interval=0
        )
        assert event.data["live_view_url"] == "https://live"
        assert http.calls[-1][3] == {"after": 0, "limit": 100}

    asyncio.run(run())


def test_wait_for_event_stops_when_run_ends_first() -> None:
    terminal = {
        "events": [
            {
                "runId": RUN_ID,
                "id": 1,
                "ts": "2026-01-01T00:00:00Z",
                "type": "run.dispatch_failed",
                "data": {},
            }
        ],
        "nextAfter": 1,
        "hasMore": False,
    }
    sync_http = FakeSyncHttp([terminal])
    with pytest.raises(RuntimeError, match="run.dispatch_failed before browser.ready"):
        Runs(sync_http).wait_for_event(RUN_ID, "browser.ready")  # type: ignore[arg-type]
    assert len(sync_http.calls) == 1

    async def run() -> None:
        async_http = FakeAsyncHttp([terminal])
        with pytest.raises(RuntimeError, match="run.dispatch_failed before browser.ready"):
            await AsyncRuns(async_http).wait_for_event(  # type: ignore[arg-type]
                RUN_ID, "browser.ready"
            )
        assert len(async_http.calls) == 1

    asyncio.run(run())


# ---------------------------------------------------------------------------
# runs create / list / events
# ---------------------------------------------------------------------------


def test_runs_create_sends_camel_case_body() -> None:
    http = FakeSyncHttp(
        [
            {
                "id": RUN_ID,
                "status": "queued",
                "model": "minimax-m3",
                "sessionId": SESSION_ID,
                "workspaceId": "00000000-0000-0000-0000-000000000003",
                "eventsUrl": f"https://api.browser-use.com/api/v4/runs/{RUN_ID}/events",
            }
        ]
    )
    runs = Runs(http)  # type: ignore[arg-type]

    created = runs.create(
        "Find pricing",
        model="minimax-m3",
        model_params={"reasoning": {"effort": "high"}},
        session_id=SESSION_ID,
        browser_settings={"proxyCountryCode": "de"},
        agentmail=True,
        attached_file_ids=["00000000-0000-0000-0000-000000000009"],
        secret_bindings=[
            SecretBinding(
                alias="github_password",
                source=InlineSecretSource(type="inline", value="not-masked"),
                allowedDomains=["github.com"],
            )
        ],
        max_cost_usd="1.50",
    )

    method, path, body, _ = http.calls[0]
    assert (method, path) == ("POST", "/runs")
    assert body == {
        "task": "Find pricing",
        "model": "minimax-m3",
        "modelParams": {"reasoning": {"effort": "high"}},
        "sessionId": SESSION_ID,
        "browserSettings": {"proxyCountryCode": "de"},
        "agentmail": True,
        "attachedFileIds": ["00000000-0000-0000-0000-000000000009"],
        "secretBindings": [
            {
                "alias": "github_password",
                "source": {"type": "inline", "value": "not-masked"},
                "allowedDomains": ["github.com"],
            }
        ],
        "maxCostUsd": "1.50",
    }
    assert str(created.id) == RUN_ID


def test_runs_list_cursor_pagination() -> None:
    http = FakeSyncHttp(
        [
            {"runs": [_run_summary("completed")], "nextCursor": "cur-2", "hasMore": True},
            {"runs": [_run_summary("completed")], "nextCursor": None, "hasMore": False},
        ]
    )
    runs = Runs(http)  # type: ignore[arg-type]

    first = runs.list(session_id=SESSION_ID, limit=1)
    assert first.has_more
    assert first.next_cursor == "cur-2"

    second = runs.list(session_id=SESSION_ID, cursor=first.next_cursor, limit=1)
    assert not second.has_more

    assert http.calls[0][3] == {"sessionId": SESSION_ID, "cursor": None, "limit": 1}
    assert http.calls[1][3] == {"sessionId": SESSION_ID, "cursor": "cur-2", "limit": 1}


def test_runs_events_delta() -> None:
    http = FakeSyncHttp(
        [
            {
                "events": [
                    {"runId": RUN_ID, "id": 1, "ts": "2026-01-01T00:00:00Z", "type": "step", "data": {}},
                    {"runId": RUN_ID, "id": 2, "ts": "2026-01-01T00:00:01Z", "type": "step", "data": {}},
                ],
                "nextAfter": 2,
                "hasMore": True,
            },
            {
                "events": [
                    {"runId": RUN_ID, "id": 3, "ts": "2026-01-01T00:00:02Z", "type": "done", "data": {}},
                ],
                "nextAfter": 3,
                "hasMore": False,
            },
        ]
    )
    runs = Runs(http)  # type: ignore[arg-type]

    first = runs.events(RUN_ID, limit=2)
    assert first.next_after == 2
    assert first.has_more

    second = runs.events(RUN_ID, after=first.next_after, limit=2)
    assert http.calls[1][3] == {"after": 2, "limit": 2}
    assert not second.has_more
    assert second.events[0].id == 3


# ---------------------------------------------------------------------------
# sessions queue
# ---------------------------------------------------------------------------


def test_sessions_send_message() -> None:
    http = FakeSyncHttp([_queued_message()])
    sessions = Sessions(http)  # type: ignore[arg-type]

    msg = sessions.send_message(SESSION_ID, "also check the careers page", interrupt=True)

    method, path, body, _ = http.calls[0]
    assert (method, path) == ("POST", f"/sessions/{SESSION_ID}/queue")
    assert body == {"text": "also check the careers page", "interrupt": True}
    assert msg.status.value == "pending"


def test_sessions_queue_list() -> None:
    http = FakeSyncHttp([{"queue": [_queued_message()]}])
    sessions = Sessions(http)  # type: ignore[arg-type]

    resp = sessions.queue(SESSION_ID)

    assert http.calls[0][:2] == ("GET", f"/sessions/{SESSION_ID}/queue")
    assert len(resp.queue) == 1


def test_sessions_get_message_and_purge() -> None:
    http = FakeSyncHttp([_queued_message(), {}])
    sessions = Sessions(http)  # type: ignore[arg-type]

    msg = sessions.get_message(SESSION_ID, 7)
    sessions.purge(SESSION_ID)

    assert msg.id == 7
    assert http.calls[0][:2] == ("GET", f"/sessions/{SESSION_ID}/queue/7")
    assert http.calls[1][:2] == ("POST", f"/sessions/{SESSION_ID}/purge")


def test_sessions_remove_message() -> None:
    http = FakeSyncHttp([_queued_message("cancelled")])
    sessions = Sessions(http)  # type: ignore[arg-type]

    msg = sessions.remove_message(SESSION_ID, 7)

    assert http.calls[0][:2] == ("DELETE", f"/sessions/{SESSION_ID}/queue/7")
    assert msg.status.value == "cancelled"


def test_sessions_list_cursor_pagination() -> None:
    http = FakeSyncHttp([{"sessions": [], "nextCursor": None, "hasMore": False}])
    sessions = Sessions(http)  # type: ignore[arg-type]

    sessions.list(cursor="xyz", limit=10)

    assert http.calls[0][3] == {"cursor": "xyz", "limit": 10}


# ---------------------------------------------------------------------------
# workspaces
# ---------------------------------------------------------------------------


def _workspace_info() -> dict[str, Any]:
    return {
        "id": WORKSPACE_ID,
        "name": "my workspace",
        "archived": False,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }


def _upload_item() -> dict[str, Any]:
    return {
        "id": UPLOAD_ID,
        "name": "data.csv",
        "storedName": "data.csv",
        "path": "uploads/data.csv",
        "willOverride": False,
        "uploadUrl": "https://s3.example/put/data.csv",
    }


def _workspace_file(path: str, url: str | None) -> dict[str, Any]:
    return {
        "path": path,
        "size": 7,
        "lastModified": "2026-01-01T00:00:00Z",
        "url": url,
    }


def test_workspaces_create() -> None:
    http = FakeSyncHttp([_workspace_info()])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    ws = workspaces.create(name="my workspace")

    method, path, body, _ = http.calls[0]
    assert (method, path) == ("POST", "/workspaces")
    assert body == {"name": "my workspace"}
    assert str(ws.id) == WORKSPACE_ID


def test_workspaces_files_cursor_pagination() -> None:
    http = FakeSyncHttp([{"files": [], "nextCursor": None, "hasMore": False}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    workspaces.files(
        WORKSPACE_ID,
        prefix="uploads/",
        limit=20,
        cursor="cur-1",
        include_urls=True,
        content_disposition="attachment",
    )

    assert http.calls[0][:2] == ("GET", f"/workspaces/{WORKSPACE_ID}/files")
    assert http.calls[0][3] == {
        "prefix": "uploads/",
        "limit": 20,
        "cursor": "cur-1",
        "includeUrls": True,
        "contentDisposition": "attachment",
    }


def test_workspaces_update_size_delete_and_delete_file() -> None:
    http = FakeSyncHttp(
        [{**_workspace_info(), "name": None}, {"usedBytes": 10, "maxBytes": 100}, {}, {}]
    )
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    updated = workspaces.update(WORKSPACE_ID, name=None)
    size = workspaces.size(WORKSPACE_ID)
    workspaces.delete_file(WORKSPACE_ID, path="uploads/data.csv")
    workspaces.delete(WORKSPACE_ID)

    assert updated.name is None
    assert size.used_bytes == 10
    assert http.calls[0][2] == {"name": None}
    assert http.calls[2][3] == {"path": "uploads/data.csv"}
    assert http.calls[3][:2] == ("DELETE", f"/workspaces/{WORKSPACE_ID}")


def test_workspaces_upload_files_presign() -> None:
    http = FakeSyncHttp([{"files": [_upload_item()]}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    from browser_use_sdk.generated.v4.models import WorkspaceFileUploadItem

    resp = workspaces.upload_files(
        WORKSPACE_ID,
        [WorkspaceFileUploadItem(name="data.csv", contentType="text/csv", size=3)],
    )

    method, path, body, _ = http.calls[0]
    assert (method, path) == ("POST", f"/workspaces/{WORKSPACE_ID}/files/upload")
    assert body == {
        "files": [{"name": "data.csv", "contentType": "text/csv", "size": 3}],
        "allowOverrides": True,
    }
    assert str(resp.files[0].id) == UPLOAD_ID


class _FakePutResponse:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"{self.status_code}", request=None, response=None  # type: ignore[arg-type]
            )


class _FakeSyncPutClient:
    """Captures PUT calls; stands in for httpx.Client in the upload helper."""

    calls: list[tuple[str, bytes, dict[str, str]]] = []
    status_code = 200

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def __enter__(self) -> _FakeSyncPutClient:
        return self

    def __exit__(self, *_args: Any) -> None:
        pass

    def put(self, url: str, *, content: bytes, headers: dict[str, str]) -> _FakePutResponse:
        type(self).calls.append((url, content, headers))
        return _FakePutResponse(type(self).status_code)


def test_workspaces_upload_reads_once_and_puts(tmp_path: Path, monkeypatch: Any) -> None:
    f = tmp_path / "data.csv"
    f.write_bytes(b"id,name\n1,a\n")

    _FakeSyncPutClient.calls = []
    _FakeSyncPutClient.status_code = 200
    monkeypatch.setattr(httpx, "Client", _FakeSyncPutClient)

    http = FakeSyncHttp([{"files": [_upload_item()]}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    result = workspaces.upload(WORKSPACE_ID, f)

    # size derived from the read buffer, not a separate stat
    _, _, body, _ = http.calls[0]
    assert body is not None
    assert body["files"][0]["size"] == len(b"id,name\n1,a\n")
    assert len(_FakeSyncPutClient.calls) == 1
    url, content, _ = _FakeSyncPutClient.calls[0]
    assert url == "https://s3.example/put/data.csv"
    assert content == b"id,name\n1,a\n"
    assert str(result[0].id) == UPLOAD_ID


def test_workspaces_upload_short_presign_raises(tmp_path: Path) -> None:
    f = tmp_path / "data.csv"
    f.write_bytes(b"x")

    http = FakeSyncHttp([{"files": []}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=r"data\.csv \(position 0\)"):
        workspaces.upload(WORKSPACE_ID, f)


def test_workspaces_upload_put_failure_raises(tmp_path: Path, monkeypatch: Any) -> None:
    f = tmp_path / "data.csv"
    f.write_bytes(b"x")

    _FakeSyncPutClient.calls = []
    _FakeSyncPutClient.status_code = 403
    monkeypatch.setattr(httpx, "Client", _FakeSyncPutClient)

    http = FakeSyncHttp([{"files": [_upload_item()]}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    with pytest.raises(httpx.HTTPStatusError):
        workspaces.upload(WORKSPACE_ID, f)


def test_workspaces_upload_no_paths_raises() -> None:
    http = FakeSyncHttp([])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    # upload() guards before any HTTP call, so this raises the explicit
    # ValueError from the SDK — not an IndexError from the fake popping an empty
    # response list (which would mean the guard never ran).
    with pytest.raises(ValueError, match="at least one file path is required"):
        workspaces.upload(WORKSPACE_ID)
    # The guard short-circuited before touching the transport.
    assert http.calls == []


class _FakeDownloadResponse:
    def __init__(
        self,
        *chunks: bytes | BaseException,
        status_code: int = 200,
        on_enter: Callable[[], None] | None = None,
    ) -> None:
        self.chunks = chunks
        self.status_code = status_code
        self.on_enter = on_enter

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://s3.example/test")
            raise httpx.HTTPStatusError(
                f"{self.status_code}",
                request=request,
                response=httpx.Response(self.status_code, request=request),
            )

    def iter_bytes(self):
        for chunk in self.chunks:
            if isinstance(chunk, BaseException):
                raise chunk
            yield chunk

    async def aiter_bytes(self):
        for chunk in self.chunks:
            if isinstance(chunk, BaseException):
                raise chunk
            yield chunk


class _FakeSyncStreamContext:
    def __init__(self, response: _FakeDownloadResponse) -> None:
        self.response = response

    def __enter__(self) -> _FakeDownloadResponse:
        if self.response.on_enter is not None:
            self.response.on_enter()
        return self.response

    def __exit__(self, *_args: Any) -> None:
        pass


class _FakeSyncDownloadClient:
    responses: dict[str, _FakeDownloadResponse] = {}
    calls: list[str] = []

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def __enter__(self) -> _FakeSyncDownloadClient:
        return self

    def __exit__(self, *_args: Any) -> None:
        pass

    def stream(self, method: str, url: str) -> _FakeSyncStreamContext:
        assert method == "GET"
        type(self).calls.append(url)
        response = type(self).responses.get(
            url, _FakeDownloadResponse(status_code=404)
        )
        return _FakeSyncStreamContext(response)


def test_workspaces_download_paginates_for_exact_path(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = "https://s3.example/get/reports/result.csv"
    _FakeSyncDownloadClient.responses = {
        url: _FakeDownloadResponse(b"id,", b"name\n1,a\n")
    }
    _FakeSyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "Client", _FakeSyncDownloadClient)

    http = FakeSyncHttp(
        [
            {
                "files": [_workspace_file("reports/result.csv.bak", None)],
                "nextCursor": "page-2",
                "hasMore": True,
            },
            {
                "files": [_workspace_file("reports/result.csv", url)],
                "nextCursor": None,
                "hasMore": False,
            },
        ]
    )
    workspaces = Workspaces(http)  # type: ignore[arg-type]
    destination = tmp_path / "exports" / "result.csv"

    result = workspaces.download(WORKSPACE_ID, "reports/result.csv", to=destination)

    assert result == destination
    assert destination.read_bytes() == b"id,name\n1,a\n"
    assert _FakeSyncDownloadClient.calls == [url]
    assert [call[3] for call in http.calls] == [
        {
            "prefix": "reports/result.csv",
            "limit": None,
            "cursor": None,
            "includeUrls": True,
            "contentDisposition": None,
        },
        {
            "prefix": "reports/result.csv",
            "limit": None,
            "cursor": "page-2",
            "includeUrls": True,
            "contentDisposition": None,
        },
    ]


def test_workspaces_download_missing_file_raises() -> None:
    http = FakeSyncHttp([{"files": [], "nextCursor": None, "hasMore": False}])
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    with pytest.raises(FileNotFoundError, match="reports/missing.csv"):
        workspaces.download(WORKSPACE_ID, "reports/missing.csv")


def test_workspaces_download_all_preserves_paths_across_pages(
    tmp_path: Path, monkeypatch: Any
) -> None:
    first_url = "https://s3.example/get/reports/first.csv"
    second_url = "https://s3.example/get/reports/nested/second.csv"
    events: list[str] = []
    _FakeSyncDownloadClient.responses = {
        first_url: _FakeDownloadResponse(
            b"first", on_enter=lambda: events.append("stream:first")
        ),
        second_url: _FakeDownloadResponse(
            b"second", on_enter=lambda: events.append("stream:second")
        ),
    }
    _FakeSyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "Client", _FakeSyncDownloadClient)

    class OrderedFakeSyncHttp(FakeSyncHttp):
        def request(
            self,
            method: str,
            path: str,
            *,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            if params is not None:
                if params["includeUrls"]:
                    events.append(f"refresh:{params['prefix']}")
                else:
                    events.append(f"list:{params['cursor']}")
            return super().request(method, path, json=json, params=params)

    http = OrderedFakeSyncHttp(
        [
            {
                "files": [_workspace_file("reports/first.csv", None)],
                "nextCursor": "page-2",
                "hasMore": True,
            },
            {
                "files": [_workspace_file("reports/first.csv", first_url)],
                "nextCursor": None,
                "hasMore": False,
            },
            {
                "files": [_workspace_file("reports/nested/second.csv", None)],
                "nextCursor": None,
                "hasMore": False,
            },
            {
                "files": [_workspace_file("reports/nested/second.csv", second_url)],
                "nextCursor": None,
                "hasMore": False,
            },
        ]
    )
    workspaces = Workspaces(http)  # type: ignore[arg-type]
    destination = tmp_path / "exports"

    result = workspaces.download_all(WORKSPACE_ID, to=destination, prefix="reports/")

    assert result == [
        (destination / "reports/first.csv").resolve(),
        (destination / "reports/nested/second.csv").resolve(),
    ]
    assert result[0].read_bytes() == b"first"
    assert result[1].read_bytes() == b"second"
    assert _FakeSyncDownloadClient.calls == [first_url, second_url]
    assert events == [
        "list:None",
        "refresh:reports/first.csv",
        "stream:first",
        "list:page-2",
        "refresh:reports/nested/second.csv",
        "stream:second",
    ]
    assert [call[3] for call in http.calls] == [
        {
            "prefix": "reports/",
            "limit": None,
            "cursor": None,
            "includeUrls": None,
            "contentDisposition": None,
        },
        {
            "prefix": "reports/first.csv",
            "limit": None,
            "cursor": None,
            "includeUrls": True,
            "contentDisposition": None,
        },
        {
            "prefix": "reports/",
            "limit": None,
            "cursor": "page-2",
            "includeUrls": None,
            "contentDisposition": None,
        },
        {
            "prefix": "reports/nested/second.csv",
            "limit": None,
            "cursor": None,
            "includeUrls": True,
            "contentDisposition": None,
        },
    ]


def test_workspaces_download_all_rejects_path_traversal(
    tmp_path: Path, monkeypatch: Any
) -> None:
    _FakeSyncDownloadClient.responses = {
        "https://s3.example/get/escape": _FakeDownloadResponse(b"escape")
    }
    _FakeSyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "Client", _FakeSyncDownloadClient)

    http = FakeSyncHttp(
        [
            {
                "files": [_workspace_file("../escape.txt", None)],
                "nextCursor": None,
                "hasMore": False,
            }
        ]
    )
    workspaces = Workspaces(http)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Path traversal detected"):
        workspaces.download_all(WORKSPACE_ID, to=tmp_path / "exports")
    assert _FakeSyncDownloadClient.calls == []


def test_workspaces_download_failure_keeps_destination_and_removes_temp(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = "https://s3.example/get/reports/result.csv"
    _FakeSyncDownloadClient.responses = {
        url: _FakeDownloadResponse(
            b"partial", RuntimeError("connection dropped")
        )
    }
    _FakeSyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "Client", _FakeSyncDownloadClient)
    http = FakeSyncHttp(
        [
            {
                "files": [_workspace_file("reports/result.csv", url)],
                "nextCursor": None,
                "hasMore": False,
            }
        ]
    )
    workspaces = Workspaces(http)  # type: ignore[arg-type]
    destination = tmp_path / "exports" / "result.csv"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"previous")

    with pytest.raises(RuntimeError, match="connection dropped"):
        workspaces.download(
            WORKSPACE_ID, "reports/result.csv", to=destination
        )

    assert destination.read_bytes() == b"previous"
    assert list(destination.parent.glob(".result.csv.*.tmp")) == []


class _FakeAsyncPutClient:
    calls: list[tuple[str, bytes, dict[str, str]]] = []
    status_code = 200

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    async def __aenter__(self) -> _FakeAsyncPutClient:
        return self

    async def __aexit__(self, *_args: Any) -> None:
        pass

    async def put(self, url: str, *, content: bytes, headers: dict[str, str]) -> _FakePutResponse:
        type(self).calls.append((url, content, headers))
        return _FakePutResponse(type(self).status_code)


class _FakeAsyncStreamContext:
    def __init__(self, response: _FakeDownloadResponse) -> None:
        self.response = response

    async def __aenter__(self) -> _FakeDownloadResponse:
        if self.response.on_enter is not None:
            self.response.on_enter()
        return self.response

    async def __aexit__(self, *_args: Any) -> None:
        pass


class _FakeAsyncDownloadClient:
    responses: dict[str, _FakeDownloadResponse] = {}
    calls: list[str] = []

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    async def __aenter__(self) -> _FakeAsyncDownloadClient:
        return self

    async def __aexit__(self, *_args: Any) -> None:
        pass

    def stream(self, method: str, url: str) -> _FakeAsyncStreamContext:
        assert method == "GET"
        type(self).calls.append(url)
        response = type(self).responses.get(
            url, _FakeDownloadResponse(status_code=404)
        )
        return _FakeAsyncStreamContext(response)


def test_async_workspaces_upload(tmp_path: Path, monkeypatch: Any) -> None:
    f = tmp_path / "data.csv"
    f.write_bytes(b"id,name\n1,a\n")

    _FakeAsyncPutClient.calls = []
    _FakeAsyncPutClient.status_code = 200
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncPutClient)

    async def run() -> None:
        http = FakeAsyncHttp([{"files": [_upload_item()]}])
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]

        result = await workspaces.upload(WORKSPACE_ID, f)

        assert len(_FakeAsyncPutClient.calls) == 1
        url, content, _ = _FakeAsyncPutClient.calls[0]
        assert url == "https://s3.example/put/data.csv"
        assert content == b"id,name\n1,a\n"
        assert str(result[0].id) == UPLOAD_ID

    asyncio.run(run())


def test_async_workspaces_upload_short_presign_raises(tmp_path: Path) -> None:
    f = tmp_path / "data.csv"
    f.write_bytes(b"x")

    async def run() -> None:
        http = FakeAsyncHttp([{"files": []}])
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match=r"data\.csv \(position 0\)"):
            await workspaces.upload(WORKSPACE_ID, f)

    asyncio.run(run())


def test_async_workspaces_download_all(tmp_path: Path, monkeypatch: Any) -> None:
    first_url = "https://s3.example/get/reports/first.csv"
    second_url = "https://s3.example/get/reports/nested/second.csv"
    _FakeAsyncDownloadClient.responses = {
        first_url: _FakeDownloadResponse(b"first"),
        second_url: _FakeDownloadResponse(b"second"),
    }
    _FakeAsyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncDownloadClient)
    event_loop_thread = threading.get_ident()
    path_resolution_threads: list[int] = []
    original_safe_join = workspaces_module._safe_join

    def recording_safe_join(base: Path, untrusted: str) -> Path:
        path_resolution_threads.append(threading.get_ident())
        return original_safe_join(base, untrusted)

    monkeypatch.setattr(workspaces_module, "_safe_join", recording_safe_join)

    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {
                    "files": [_workspace_file("reports/first.csv", None)],
                    "nextCursor": "page-2",
                    "hasMore": True,
                },
                {
                    "files": [_workspace_file("reports/first.csv", first_url)],
                    "nextCursor": None,
                    "hasMore": False,
                },
                {
                    "files": [
                        _workspace_file("reports/nested/second.csv", None)
                    ],
                    "nextCursor": None,
                    "hasMore": False,
                },
                {
                    "files": [
                        _workspace_file(
                            "reports/nested/second.csv", second_url
                        )
                    ],
                    "nextCursor": None,
                    "hasMore": False,
                },
            ]
        )
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]
        destination = tmp_path / "exports"

        result = await workspaces.download_all(
            WORKSPACE_ID, to=destination, prefix="reports/"
        )

        assert result == [
            (destination / "reports/first.csv").resolve(),
            (destination / "reports/nested/second.csv").resolve(),
        ]
        assert result[0].read_bytes() == b"first"
        assert result[1].read_bytes() == b"second"
        assert _FakeAsyncDownloadClient.calls == [first_url, second_url]
        assert path_resolution_threads
        assert event_loop_thread not in path_resolution_threads
        assert [call[3] for call in http.calls] == [
            {
                "prefix": "reports/",
                "limit": None,
                "cursor": None,
                "includeUrls": None,
                "contentDisposition": None,
            },
            {
                "prefix": "reports/first.csv",
                "limit": None,
                "cursor": None,
                "includeUrls": True,
                "contentDisposition": None,
            },
            {
                "prefix": "reports/",
                "limit": None,
                "cursor": "page-2",
                "includeUrls": None,
                "contentDisposition": None,
            },
            {
                "prefix": "reports/nested/second.csv",
                "limit": None,
                "cursor": None,
                "includeUrls": True,
                "contentDisposition": None,
            },
        ]

    asyncio.run(run())


def test_async_workspaces_download_paginates_for_exact_path(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = "https://s3.example/get/reports/result.csv"
    _FakeAsyncDownloadClient.responses = {
        url: _FakeDownloadResponse(b"result")
    }
    _FakeAsyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncDownloadClient)

    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {
                    "files": [_workspace_file("reports/result.csv.bak", None)],
                    "nextCursor": "page-2",
                    "hasMore": True,
                },
                {
                    "files": [_workspace_file("reports/result.csv", url)],
                    "nextCursor": None,
                    "hasMore": False,
                },
            ]
        )
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]
        destination = tmp_path / "result.csv"

        result = await workspaces.download(
            WORKSPACE_ID, "reports/result.csv", to=destination
        )

        assert result == destination
        assert destination.read_bytes() == b"result"
        assert [call[3] for call in http.calls] == [
            {
                "prefix": "reports/result.csv",
                "limit": None,
                "cursor": None,
                "includeUrls": True,
                "contentDisposition": None,
            },
            {
                "prefix": "reports/result.csv",
                "limit": None,
                "cursor": "page-2",
                "includeUrls": True,
                "contentDisposition": None,
            },
        ]

    asyncio.run(run())


def test_async_workspaces_download_all_rejects_path_traversal(
    tmp_path: Path, monkeypatch: Any
) -> None:
    _FakeAsyncDownloadClient.responses = {}
    _FakeAsyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncDownloadClient)

    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {
                    "files": [_workspace_file("../escape.txt", None)],
                    "nextCursor": None,
                    "hasMore": False,
                }
            ]
        )
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="Path traversal detected"):
            await workspaces.download_all(
                WORKSPACE_ID, to=tmp_path / "exports"
            )
        assert _FakeAsyncDownloadClient.calls == []

    asyncio.run(run())


def test_async_workspaces_download_failure_cleans_temp(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = "https://s3.example/get/reports/result.csv"
    _FakeAsyncDownloadClient.responses = {
        url: _FakeDownloadResponse(
            b"partial", RuntimeError("connection dropped")
        )
    }
    _FakeAsyncDownloadClient.calls = []
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncDownloadClient)

    async def run() -> None:
        http = FakeAsyncHttp(
            [
                {
                    "files": [_workspace_file("reports/result.csv", url)],
                    "nextCursor": None,
                    "hasMore": False,
                }
            ]
        )
        workspaces = AsyncWorkspaces(http)  # type: ignore[arg-type]
        destination = tmp_path / "exports" / "result.csv"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"previous")

        with pytest.raises(RuntimeError, match="connection dropped"):
            await workspaces.download(
                WORKSPACE_ID, "reports/result.csv", to=destination
            )

        assert destination.read_bytes() == b"previous"
        assert list(destination.parent.glob(".result.csv.*.tmp")) == []

    asyncio.run(run())
