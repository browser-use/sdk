import httpx

from browser_use_sdk._core.http import SyncHttpClient, _clean_params


def test_clean_params_repeats_sequence_values() -> None:
    cleaned = _clean_params(
        {
            "metadata": ["team", "env=prod"],
            "pageSize": 10,
            "includeUrls": False,
            "cursor": None,
        }
    )
    assert cleaned == {
        "metadata": ["team", "env=prod"],
        "pageSize": "10",
        "includeUrls": "false",
    }
    assert httpx.QueryParams(cleaned).multi_items() == [
        ("metadata", "team"),
        ("metadata", "env=prod"),
        ("pageSize", "10"),
        ("includeUrls", "false"),
    ]


def test_request_forwards_headers_alongside_authentication() -> None:
    requested_headers = httpx.Headers()

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requested_headers
        requested_headers = request.headers
        return httpx.Response(200, json={})

    client = SyncHttpClient("https://api.example.com", "test")
    client._client.close()
    client._client = httpx.Client(
        base_url="https://api.example.com",
        headers={"X-Browser-Use-API-Key": "test"},
        transport=httpx.MockTransport(handler),
    )
    try:
        client.request(
            "POST",
            "/sessions/id/queue",
            json={"text": "hello"},
            headers={"X-V4-Queue-Deduplicate": "exact-text-v1"},
        )
    finally:
        client.close()

    assert requested_headers["X-V4-Queue-Deduplicate"] == "exact-text-v1"
    assert requested_headers["X-Browser-Use-API-Key"] == "test"
