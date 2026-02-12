from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, overload

from pydantic import BaseModel

from .._core.http import AsyncHttpClient, SyncHttpClient
from .resources.billing import AsyncBilling, Billing
from .resources.browsers import AsyncBrowsers, Browsers
from .resources.files import AsyncFiles, Files
from .resources.marketplace import AsyncMarketplace, Marketplace
from .resources.profiles import AsyncProfiles, Profiles
from .resources.sessions import AsyncSessions, Sessions
from .resources.skills import AsyncSkills, Skills
from .resources.tasks import AsyncTasks, Tasks
from .helpers import AsyncTaskHandle, TaskHandle

_V2_BASE_URL = "https://api.browser-use.com/api/v2"

T = TypeVar("T")


class BrowserUse:
    """Synchronous Browser Use v2 client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = SyncHttpClient(
            base_url=base_url or _V2_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.billing = Billing(self._http)
        self.tasks = Tasks(self._http)
        self.sessions = Sessions(self._http)
        self.files = Files(self._http)
        self.profiles = Profiles(self._http)
        self.browsers = Browsers(self._http)
        self.skills = Skills(self._http)
        self.marketplace = Marketplace(self._http)

    @overload
    def run(
        self,
        task: str,
        *,
        output_schema: Type[T],
        session_id: Optional[str] = ...,
        llm: Optional[str] = ...,
        start_url: Optional[str] = ...,
        max_steps: Optional[int] = ...,
        **extra: Any,
    ) -> TaskHandle[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        session_id: Optional[str] = ...,
        llm: Optional[str] = ...,
        start_url: Optional[str] = ...,
        max_steps: Optional[int] = ...,
        **extra: Any,
    ) -> TaskHandle[str]: ...

    def run(
        self,
        task: str,
        *,
        output_schema: Optional[Type[Any]] = None,
        session_id: Optional[str] = None,
        llm: Optional[str] = None,
        start_url: Optional[str] = None,
        max_steps: Optional[int] = None,
        **extra: Any,
    ) -> TaskHandle[Any]:
        """Create a task and return a TaskHandle for polling/streaming.

        When ``output_schema`` is a Pydantic BaseModel subclass, the SDK
        automatically converts it to a JSON schema string for the API and
        the returned handle can parse the output via ``handle.parse_output()``.

        Example::

            handle = client.run("Find the top HN post")
            result = handle.complete()

        With structured output::

            class Product(BaseModel):
                name: str
                price: float

            handle = client.run("Find product info", output_schema=Product)
            result = handle.complete()
            product = handle.parse_output(result)  # Product instance
        """
        if output_schema is not None and issubclass(output_schema, BaseModel):
            extra["structured_output"] = json.dumps(output_schema.model_json_schema())

        data = self.tasks.create(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
            **extra,
        )
        return TaskHandle(data, self.tasks, output_schema)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> BrowserUse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncBrowserUse:
    """Asynchronous Browser Use v2 client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = AsyncHttpClient(
            base_url=base_url or _V2_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.billing = AsyncBilling(self._http)
        self.tasks = AsyncTasks(self._http)
        self.sessions = AsyncSessions(self._http)
        self.files = AsyncFiles(self._http)
        self.profiles = AsyncProfiles(self._http)
        self.browsers = AsyncBrowsers(self._http)
        self.skills = AsyncSkills(self._http)
        self.marketplace = AsyncMarketplace(self._http)

    @overload
    async def run(
        self,
        task: str,
        *,
        output_schema: Type[T],
        session_id: Optional[str] = ...,
        llm: Optional[str] = ...,
        start_url: Optional[str] = ...,
        max_steps: Optional[int] = ...,
        **extra: Any,
    ) -> AsyncTaskHandle[T]: ...

    @overload
    async def run(
        self,
        task: str,
        *,
        session_id: Optional[str] = ...,
        llm: Optional[str] = ...,
        start_url: Optional[str] = ...,
        max_steps: Optional[int] = ...,
        **extra: Any,
    ) -> AsyncTaskHandle[str]: ...

    async def run(
        self,
        task: str,
        *,
        output_schema: Optional[Type[Any]] = None,
        session_id: Optional[str] = None,
        llm: Optional[str] = None,
        start_url: Optional[str] = None,
        max_steps: Optional[int] = None,
        **extra: Any,
    ) -> AsyncTaskHandle[Any]:
        """Create a task and return an AsyncTaskHandle for polling/streaming.

        When ``output_schema`` is a Pydantic BaseModel subclass, the SDK
        automatically converts it to a JSON schema string for the API and
        the returned handle can parse the output via ``handle.parse_output()``.

        Example::

            handle = await client.run("Find the top HN post")
            result = await handle.complete()

        With structured output::

            class Product(BaseModel):
                name: str
                price: float

            handle = await client.run("Find product info", output_schema=Product)
            result = await handle.complete()
            product = handle.parse_output(result)  # Product instance
        """
        if output_schema is not None and issubclass(output_schema, BaseModel):
            extra["structured_output"] = json.dumps(output_schema.model_json_schema())

        data = await self.tasks.create(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
            **extra,
        )
        return AsyncTaskHandle(data, self.tasks, output_schema)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncBrowserUse:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
