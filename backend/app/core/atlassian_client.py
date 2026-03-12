"""HTTP client for Atlassian Cloud REST APIs with retry and error handling."""

import asyncio
import httpx
import logging
from typing import Any, Optional
from .config import settings

logger = logging.getLogger(__name__)


class AtlassianAPIError(Exception):
    """Raised when an Atlassian API call fails."""

    def __init__(self, message: str, status_code: int | None = None, url: str = ""):
        self.status_code = status_code
        self.url = url
        super().__init__(message)


class AtlassianClient:
    """HTTP client for Atlassian Cloud REST APIs with retry, timeout, and batching."""

    MAX_RETRIES = 3
    RETRY_BACKOFF = [1, 2, 4]

    def __init__(self):
        self._auth = (settings.ATLASSIAN_EMAIL, settings.ATLASSIAN_API_TOKEN)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            auth=self._auth,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def get(self, url: str, params: Optional[dict] = None) -> Any:
        """GET with automatic retry on transient failures and rate-limit handling."""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self._client() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 429:
                        retry_after = int(resp.headers.get("Retry-After", 5))
                        logger.warning(f"Rate limited on {url}, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    resp.raise_for_status()
                    return resp.json()
            except httpx.HTTPStatusError as e:
                raise AtlassianAPIError(
                    f"HTTP {e.response.status_code}: {e.response.text[:300]}",
                    status_code=e.response.status_code,
                    url=url,
                )
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait = self.RETRY_BACKOFF[attempt]
                    logger.warning(f"Retry {attempt + 1}/{self.MAX_RETRIES} for {url} after {wait}s")
                    await asyncio.sleep(wait)
            except Exception as e:
                raise AtlassianAPIError(f"Unexpected error calling {url}: {e}", url=url)

        raise AtlassianAPIError(
            f"Failed after {self.MAX_RETRIES} retries: {last_error}",
            url=url,
        )

    async def get_paginated(
        self, url: str, params: Optional[dict] = None, max_results: int = 1000
    ) -> list[Any]:
        """Fetch all pages from a paginated Atlassian REST endpoint."""
        results = []
        params = params or {}
        start_at = 0
        page_size = min(100, max_results)

        while len(results) < max_results:
            params.update({"startAt": start_at, "maxResults": page_size})
            try:
                data = await self.get(url, params)
            except AtlassianAPIError as e:
                logger.warning(f"Pagination stopped at offset {start_at} for {url}: {e}")
                break

            values = data.get("values", data.get("results", []))
            if not values:
                break

            results.extend(values)
            total = data.get("total", len(results))
            start_at += len(values)

            if start_at >= total:
                break

        return results[:max_results]

    async def batch(self, items: list, fetch_fn, concurrency: int = 5) -> list:
        """Run fetch_fn(item) for each item with bounded concurrency.

        Returns list of (item, result | None) tuples. Failed items return None
        without breaking the batch.
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def _fetch(item):
            async with semaphore:
                try:
                    return item, await fetch_fn(item)
                except Exception as e:
                    logger.warning(f"Batch fetch failed for {item}: {e}")
                    return item, None

        return list(await asyncio.gather(*[_fetch(i) for i in items]))

    # --- Jira helpers ---

    async def jira_get(self, path: str, params: Optional[dict] = None) -> Any:
        return await self.get(f"{settings.jira_rest_url}{path}", params)

    async def jira_search(self, jql: str, fields: str = "*all", max_results: int = 100) -> list[dict]:
        return await self.get_paginated(
            f"{settings.jira_rest_url}/search",
            params={"jql": jql, "fields": fields},
            max_results=max_results,
        )

    # --- Confluence helpers ---

    async def confluence_get(self, path: str, params: Optional[dict] = None) -> Any:
        return await self.get(f"{settings.confluence_rest_url}{path}", params)

    # --- JSM helpers ---

    async def jsm_get(self, path: str, params: Optional[dict] = None) -> Any:
        return await self.get(f"{settings.jsm_rest_url}{path}", params)


atlassian_client = AtlassianClient()
