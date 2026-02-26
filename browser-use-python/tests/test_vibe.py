"""Spec-driven vibe test.

Reads the OpenAPI specs at runtime and verifies every endpoint
has a corresponding SDK method.
"""

from __future__ import annotations

import inspect
import json
import typing
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import pytest

# ---------------------------------------------------------------------------
# Locate spec files via CLOUD_REPO_PATH in .env
# ---------------------------------------------------------------------------
_SDK_REPO = Path(__file__).resolve().parents[2]  # browser-use-python/tests -> sdk repo root


def _get_cloud_repo_path() -> Path:
    env_file = _SDK_REPO / ".env"
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("CLOUD_REPO_PATH=") and not line.startswith("#"):
            return Path(line.split("=", 1)[1].strip())
    raise RuntimeError("CLOUD_REPO_PATH not found in .env")


_CLOUD = _get_cloud_repo_path()
_V2_SPEC = _CLOUD / "backend" / "spec" / "api" / "v2" / "openapi.json"
_V3_SPEC = _CLOUD / "backend" / "spec" / "api" / "v3" / "openapi.json"


def _load_spec(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Endpoint -> SDK mapping
# ---------------------------------------------------------------------------

# Each entry: (http_method, path_pattern) -> (resource_attr, method_name)
_V2_MAP: Dict[Tuple[str, str], Tuple[str, str]] = {
    # billing
    ("get", "/billing/account"): ("billing", "account"),
    # tasks
    ("post", "/tasks"): ("tasks", "create"),
    ("get", "/tasks"): ("tasks", "list"),
    ("get", "/tasks/{task_id}"): ("tasks", "get"),
    ("patch", "/tasks/{task_id}"): ("tasks", "stop"),
    ("get", "/tasks/{task_id}/status"): ("tasks", "status"),
    ("get", "/tasks/{task_id}/logs"): ("tasks", "logs"),
    # sessions
    ("post", "/sessions"): ("sessions", "create"),
    ("get", "/sessions"): ("sessions", "list"),
    ("get", "/sessions/{session_id}"): ("sessions", "get"),
    ("patch", "/sessions/{session_id}"): ("sessions", "stop"),
    ("delete", "/sessions/{session_id}"): ("sessions", "delete"),
    ("get", "/sessions/{session_id}/public-share"): ("sessions", "get_share"),
    ("post", "/sessions/{session_id}/public-share"): ("sessions", "create_share"),
    ("delete", "/sessions/{session_id}/public-share"): ("sessions", "delete_share"),
    ("post", "/sessions/{session_id}/purge"): ("sessions", "purge"),
    # files
    ("post", "/files/sessions/{session_id}/presigned-url"): ("files", "session_url"),
    ("post", "/files/browsers/{session_id}/presigned-url"): ("files", "browser_url"),
    ("get", "/files/tasks/{task_id}/output-files/{file_id}"): ("files", "task_output"),
    # profiles
    ("post", "/profiles"): ("profiles", "create"),
    ("get", "/profiles"): ("profiles", "list"),
    ("get", "/profiles/{profile_id}"): ("profiles", "get"),
    ("patch", "/profiles/{profile_id}"): ("profiles", "update"),
    ("delete", "/profiles/{profile_id}"): ("profiles", "delete"),
    # browsers
    ("post", "/browsers"): ("browsers", "create"),
    ("get", "/browsers"): ("browsers", "list"),
    ("get", "/browsers/{session_id}"): ("browsers", "get"),
    ("patch", "/browsers/{session_id}"): ("browsers", "stop"),
    # skills
    ("post", "/skills"): ("skills", "create"),
    ("get", "/skills"): ("skills", "list"),
    ("get", "/skills/{skill_id}"): ("skills", "get"),
    ("patch", "/skills/{skill_id}"): ("skills", "update"),
    ("delete", "/skills/{skill_id}"): ("skills", "delete"),
    ("post", "/skills/{skill_id}/cancel"): ("skills", "cancel"),
    ("post", "/skills/{skill_id}/execute"): ("skills", "execute"),
    ("post", "/skills/{skill_id}/refine"): ("skills", "refine"),
    ("post", "/skills/{skill_id}/rollback"): ("skills", "rollback"),
    ("get", "/skills/{skill_id}/executions"): ("skills", "executions"),
    ("get", "/skills/{skill_id}/executions/{execution_id}/output"): ("skills", "execution_output"),
    # marketplace
    ("get", "/marketplace/skills"): ("marketplace", "list"),
    ("get", "/marketplace/skills/{skill_slug}"): ("marketplace", "get"),
    ("post", "/marketplace/skills/{skill_id}/clone"): ("marketplace", "clone"),
    ("post", "/marketplace/skills/{skill_id}/execute"): ("marketplace", "execute"),
}

_V3_MAP: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("post", "/sessions"): ("sessions", "create"),
    ("get", "/sessions"): ("sessions", "list"),
    ("get", "/sessions/{session_id}"): ("sessions", "get"),
    ("delete", "/sessions/{session_id}"): ("sessions", "delete"),
    ("post", "/sessions/{session_id}/stop"): ("sessions", "stop"),
    ("get", "/sessions/{session_id}/files"): ("sessions", "files"),
    ("post", "/sessions/{session_id}/files/upload"): ("sessions", "upload_files"),
}

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _spec_endpoints(spec: Dict[str, Any]) -> Set[Tuple[str, str]]:
    endpoints: Set[Tuple[str, str]] = set()
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.lower() in _HTTP_METHODS:
                endpoints.add((method.lower(), path))
    return endpoints


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestV2Coverage:
    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.spec = _load_spec(_V2_SPEC)

    def test_all_spec_endpoints_mapped(self) -> None:
        spec_eps = _spec_endpoints(self.spec)
        mapped = set(_V2_MAP.keys())
        missing = spec_eps - mapped
        assert not missing, f"Unmapped v2 endpoints: {missing}"

    def test_sdk_methods_exist(self) -> None:
        from browser_use_sdk.v2.client import BrowserUse

        client = BrowserUse.__new__(BrowserUse)
        # Manually set up resource stubs so we can inspect
        from browser_use_sdk.v2 import resources

        for resource_attr, method_name in _V2_MAP.values():
            # Check resource class has the method
            resource_classes = {
                "billing": resources.Billing,
                "tasks": resources.Tasks,
                "sessions": resources.Sessions,
                "files": resources.Files,
                "profiles": resources.Profiles,
                "browsers": resources.Browsers,
                "skills": resources.Skills,
                "marketplace": resources.Marketplace,
            }
            cls = resource_classes[resource_attr]
            assert hasattr(cls, method_name), (
                f"{cls.__name__} missing method '{method_name}'"
            )
            method = getattr(cls, method_name)
            assert callable(method), (
                f"{cls.__name__}.{method_name} is not callable"
            )

    def test_async_sdk_methods_exist(self) -> None:
        from browser_use_sdk.v2 import resources

        async_classes = {
            "billing": resources.AsyncBilling,
            "tasks": resources.AsyncTasks,
            "sessions": resources.AsyncSessions,
            "files": resources.AsyncFiles,
            "profiles": resources.AsyncProfiles,
            "browsers": resources.AsyncBrowsers,
            "skills": resources.AsyncSkills,
            "marketplace": resources.AsyncMarketplace,
        }
        for resource_attr, method_name in _V2_MAP.values():
            cls = async_classes[resource_attr]
            assert hasattr(cls, method_name), (
                f"{cls.__name__} missing method '{method_name}'"
            )
            method = getattr(cls, method_name)
            assert inspect.iscoroutinefunction(method), (
                f"{cls.__name__}.{method_name} should be async"
            )


class TestV3Coverage:
    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.spec = _load_spec(_V3_SPEC)

    def test_all_spec_endpoints_mapped(self) -> None:
        spec_eps = _spec_endpoints(self.spec)
        mapped = set(_V3_MAP.keys())
        missing = spec_eps - mapped
        assert not missing, f"Unmapped v3 endpoints: {missing}"

    def test_sdk_methods_exist(self) -> None:
        from browser_use_sdk.v3.resources import sessions

        for _, method_name in _V3_MAP.values():
            assert hasattr(sessions.Sessions, method_name), (
                f"Sessions missing method '{method_name}'"
            )

    def test_async_sdk_methods_exist(self) -> None:
        from browser_use_sdk.v3.resources import sessions

        for _, method_name in _V3_MAP.values():
            assert hasattr(sessions.AsyncSessions, method_name), (
                f"AsyncSessions missing method '{method_name}'"
            )
            method = getattr(sessions.AsyncSessions, method_name)
            assert inspect.iscoroutinefunction(method), (
                f"AsyncSessions.{method_name} should be async"
            )


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _get_resource_classes() -> Dict[str, Any]:
    from browser_use_sdk.v2 import resources

    return {
        "billing": resources.Billing,
        "tasks": resources.Tasks,
        "sessions": resources.Sessions,
        "files": resources.Files,
        "profiles": resources.Profiles,
        "browsers": resources.Browsers,
        "skills": resources.Skills,
        "marketplace": resources.Marketplace,
    }


def _get_async_resource_classes() -> Dict[str, Any]:
    from browser_use_sdk.v2 import resources

    return {
        "billing": resources.AsyncBilling,
        "tasks": resources.AsyncTasks,
        "sessions": resources.AsyncSessions,
        "files": resources.AsyncFiles,
        "profiles": resources.AsyncProfiles,
        "browsers": resources.AsyncBrowsers,
        "skills": resources.AsyncSkills,
        "marketplace": resources.AsyncMarketplace,
    }


class TestSpecDrift:
    """Verify SDK methods match the OpenAPI spec in detail — params, return types, action variants."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.spec = _load_spec(_V2_SPEC)

    def _get_query_params(self, method: str, path: str) -> Set[str]:
        op = self.spec["paths"].get(path, {}).get(method, {})
        return {
            p["name"]
            for p in op.get("parameters", [])
            if p.get("in") == "query"
        }

    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        parts = ref.lstrip("#/").split("/")
        obj: Any = self.spec
        for part in parts:
            obj = obj[part]
        return obj

    def _get_response_schema_name(self, method: str, path: str) -> str | None:
        op = self.spec["paths"].get(path, {}).get(method, {})
        for status in ("200", "201"):
            resp = op.get("responses", {}).get(status, {})
            content = resp.get("content", {}).get("application/json", {})
            ref = content.get("schema", {}).get("$ref", "")
            if ref:
                return ref.split("/")[-1]
        return None

    def _get_action_enum(self, method: str, path: str) -> List[str]:
        op = self.spec["paths"].get(path, {}).get(method, {})
        body = op.get("requestBody", {})
        content = body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})
        if "$ref" in schema:
            schema = self._resolve_ref(schema["$ref"])
        props = schema.get("properties", {})
        action = props.get("action", {})
        if "$ref" in action:
            action = self._resolve_ref(action["$ref"])
        return action.get("enum", [])

    # -- Query parameter completeness --

    def test_query_params_complete(self) -> None:
        """Every spec query param should have a matching SDK method parameter."""
        classes = _get_resource_classes()
        missing: List[str] = []

        for (method, path), (resource_attr, method_name) in _V2_MAP.items():
            spec_params = self._get_query_params(method, path)
            if not spec_params:
                continue
            cls = classes[resource_attr]
            sig = inspect.signature(getattr(cls, method_name))
            sdk_params = {
                _snake_to_camel(p)
                for p in sig.parameters
                if p not in ("self", "extra", "kwargs")
            }
            for sp in sorted(spec_params):
                if sp not in sdk_params:
                    missing.append(
                        f"{cls.__name__}.{method_name}() missing param '{sp}'"
                        f" (from {method.upper()} {path})"
                    )

        assert not missing, "Missing query params:\n" + "\n".join(missing)

    # -- Response type correctness --

    def test_response_types_match(self) -> None:
        """SDK return type should match the spec response schema name."""
        classes = _get_resource_classes()
        mismatches: List[str] = []

        for (method, path), (resource_attr, method_name) in _V2_MAP.items():
            spec_type = self._get_response_schema_name(method, path)
            if not spec_type:
                continue
            cls = classes[resource_attr]
            hints = typing.get_type_hints(getattr(cls, method_name))
            return_type = hints.get("return")
            if return_type is None or return_type is type(None):
                continue
            sdk_type_name = getattr(return_type, "__name__", str(return_type))
            if sdk_type_name != spec_type:
                mismatches.append(
                    f"{cls.__name__}.{method_name}() returns '{sdk_type_name}'"
                    f" but spec says '{spec_type}'"
                    f" ({method.upper()} {path})"
                )

        assert not mismatches, "Return type mismatches:\n" + "\n".join(mismatches)

    # -- Action variants --

    def test_task_action_variants(self) -> None:
        """All action values for PATCH /tasks/{task_id} should have SDK methods."""
        actions = self._get_action_enum("patch", "/tasks/{task_id}")
        assert actions, "No action enum found for PATCH /tasks/{task_id}"

        action_to_method = {
            "stop": "stop",
            "stop_task_and_session": "stop_task_and_session",
        }
        missing: List[str] = []
        for action in actions:
            method_name = action_to_method.get(action)
            if not method_name:
                missing.append(f"No SDK method mapping for action '{action}'")
                continue
            for label, classes_fn in [("sync", _get_resource_classes), ("async", _get_async_resource_classes)]:
                cls = classes_fn()["tasks"]
                if not hasattr(cls, method_name):
                    missing.append(f"{cls.__name__} missing '{method_name}' for action '{action}'")

        assert not missing, "Missing action variants:\n" + "\n".join(missing)


class TestClientInit:
    def test_v2_default_import(self) -> None:
        from browser_use_sdk import BrowserUse, AsyncBrowserUse, BrowserUseError

        assert BrowserUse is not None
        assert AsyncBrowserUse is not None
        assert issubclass(BrowserUseError, Exception)

    def test_v3_import(self) -> None:
        from browser_use_sdk.v3 import BrowserUse, AsyncBrowserUse

        assert BrowserUse is not None
        assert AsyncBrowserUse is not None

    def test_v2_resources_attached(self) -> None:
        from browser_use_sdk import BrowserUse

        client = BrowserUse(api_key="test-key")
        expected = [
            "billing", "tasks", "sessions", "files",
            "profiles", "browsers", "skills", "marketplace",
        ]
        for attr in expected:
            assert hasattr(client, attr), f"BrowserUse missing .{attr}"
        client.close()

    def test_v3_resources_attached(self) -> None:
        from browser_use_sdk.v3 import BrowserUse

        client = BrowserUse(api_key="test-key")
        assert hasattr(client, "sessions")
        client.close()
