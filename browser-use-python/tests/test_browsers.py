from __future__ import annotations

from typing import Any

import pytest

from browser_use_sdk.v2.resources.browsers import Browsers as V2Browsers
from browser_use_sdk.v3.resources.browsers import Browsers as V3Browsers


class FakeHttp:
    def __init__(self) -> None:
        self.calls: list[
            tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]
        ] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, json, params))
        if method == "POST":
            return {
                "id": "00000000-0000-0000-0000-000000000001",
                "status": "active",
                "timeoutAt": "2026-08-21T20:00:00Z",
                "startedAt": "2026-08-21T19:00:00Z",
                "metadata": json["metadata"] if json else {},
            }
        return {"items": [], "totalItems": 0, "pageNumber": 1, "pageSize": 10}


@pytest.mark.parametrize("browser_cls", [V2Browsers, V3Browsers])
def test_browser_metadata_create_and_list(browser_cls: type[Any]) -> None:
    http = FakeHttp()
    browsers = browser_cls(http)

    created = browsers.create(
        metadata={"team": "sdk", "env": "test"},
        pdf_renderer_enabled=False,
        solve_captchas=False,
    )
    browsers.list(metadata=["team", "env=test"])

    assert created.metadata == {"team": "sdk", "env": "test"}
    assert http.calls[0][2] == {
        "metadata": {"team": "sdk", "env": "test"},
        "pdfRendererEnabled": False,
        "solveCaptchas": False,
    }
    assert http.calls[1][3] == {
        "pageSize": None,
        "pageNumber": None,
        "filterBy": None,
        "agentSessionId": None,
        "metadata": ["team", "env=test"],
    }


@pytest.mark.parametrize("browser_cls", [V2Browsers, V3Browsers])
def test_browser_metadata_rejects_more_than_10_entries(browser_cls: type[Any]) -> None:
    http = FakeHttp()
    browsers = browser_cls(http)
    metadata = {f"key-{index}": f"value-{index}" for index in range(11)}

    with pytest.raises(ValueError, match="metadata supports at most 10"):
        browsers.create(metadata=metadata)

    assert http.calls == []
