from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Protocol

import os

import httpx


class FinnhubClientError(Exception):
    """Raised when Finnhub API calls fail or return unexpected data."""

class FinnhubForbiddenError(FinnhubClientError):
    """Raised when Finnhub returns 403 (endpoint not included on current API plan)."""

class FinnhubClient(Protocol):
    """Protocol for Finnhub API client implementations."""

    async def fetch_company_news(
        self,
        symbol: str,
        date_from: str,
        date_to: str,
    ) -> List[Dict[str, Any]]:
        """Fetch company news items for a date range (GET /company-news)."""
        ...

    async def fetch_recommendation_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch analyst recommendation trends (GET /stock/recommendation)."""
        ...


@dataclass
class HttpFinnhubClient:
    """
    Finnhub client.
    """

    api_key: Optional[str] = field(default_factory=lambda: os.getenv("FINNHUB_API_KEY"))
    base_url: str = "https://finnhub.io/api/v1"
    timeout: float = 20.0

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.api_key:
            raise FinnhubClientError("FINNHUB_API_KEY is not set in environment variables.")

        query: Dict[str, Any] = {**(params or {}), "token": self.api_key}
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=query)
            except httpx.RequestError as e:
                raise FinnhubClientError(f"Finnhub request failed for '{path}': {e}") from e

        if response.status_code == 401:
            raise FinnhubClientError(
                "Finnhub authentication failed (401). Check FINNHUB_API_KEY."
            )
        if response.status_code == 403:
            raise FinnhubForbiddenError(
                f"Finnhub endpoint '{path}' returned 403 — not included on this API plan."
            )
        if response.status_code == 429:
            raise FinnhubClientError(
                "Finnhub rate limit exceeded (429). Back off and retry later."
            )
        if response.status_code >= 500:
            raise FinnhubClientError(
                f"Finnhub server error ({response.status_code}) for '{path}'."
            )
        if response.status_code >= 400:
            raise FinnhubClientError(
                f"Finnhub API error ({response.status_code}) for '{path}': {response.text[:300]}"
            )

        try:
            return response.json()
        except ValueError as e:
            raise FinnhubClientError(f"Finnhub returned non-JSON for '{path}'.") from e

    async def fetch_company_news(
        self,
        symbol: str,
        date_from: str,
        date_to: str,
    ) -> List[Dict[str, Any]]:
        """Fetch company news headlines for an inclusive YYYY-MM-DD window."""
        payload = await self._get(
            "company-news",
            {
                "symbol": symbol.upper(),
                "from": date_from,
                "to": date_to,
            },
        )
        if not isinstance(payload, list):
            raise FinnhubClientError("Finnhub company-news response must be a JSON array.")
        return payload

    async def fetch_recommendation_trends(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch analyst buy/hold/sell trend rows (GET /stock/recommendation)."""
        payload = await self._get("stock/recommendation", {"symbol": symbol.upper()})
        if not isinstance(payload, list):
            raise FinnhubClientError("Finnhub stock/recommendation response must be a JSON array.")
        return payload


def default_company_news_window(days: int = 7) -> tuple[str, str]:
    """Return (from_date, to_date)"""
    end = date.today()
    start = end - timedelta(days=max(days - 1, 0))
    return start.isoformat(), end.isoformat()
