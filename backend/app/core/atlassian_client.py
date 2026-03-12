import httpx
from typing import Any, Optional
from .config import settings


class AtlassianClient:
    """HTTP client for Atlassian Cloud REST APIs."""

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
        async with self._client() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

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
            data = await self.get(url, params)

            values = data.get("values", data.get("results", []))
            if not values:
                break

            results.extend(values)
            total = data.get("total", len(results))
            start_at += len(values)

            if start_at >= total:
                break

        return results[:max_results]

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
