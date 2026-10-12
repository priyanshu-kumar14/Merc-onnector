"""Small Zoho Inventory API client with OAuth refresh and bounded retries."""
import random
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from .config import Settings

class ZohoAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

class ZohoClient:
    def __init__(self, settings: Settings, http: httpx.Client | None = None,
                 token_http: httpx.Client | None = None, sleep=time.sleep):
        self.settings = settings
        self.http = http or httpx.Client(timeout=settings.timeout_seconds)
        self.token_http = token_http or httpx.Client(timeout=settings.timeout_seconds)
        self._sleep = sleep
        self._access_token: str | None = None

    def _refresh_access_token(self) -> str:
        url = f"{self.settings.accounts_url}/oauth/v2/token"
        try:
            response = self.token_http.post(url, data={
                "grant_type": "refresh_token",
                "client_id": self.settings.client_id,
                "client_secret": self.settings.client_secret,
                "refresh_token": self.settings.refresh_token,
            })
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ZohoAPIError("Unable to refresh Zoho access token; verify OAuth settings and data-center URL") from exc
        token = payload.get("access_token")
        if not token:
            # Do not echo the provider response: it may contain sensitive details.
            raise ZohoAPIError("Zoho token response did not contain an access_token")
        self._access_token = token
        return token

    @staticmethod
    def _retry_delay(response: httpx.Response | None, attempt: int) -> float:
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return min(30.0, max(0.0, float(retry_after)))
                except ValueError:
                    pass
        return min(8.0, 0.5 * (2 ** attempt) + random.uniform(0, 0.25))

    def request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        # Only internal, fixed endpoint paths should be passed to this method.
        token = self._access_token or self._refresh_access_token()
        query = dict(params or {})
        query["organization_id"] = self.settings.organization_id
        url = f"{self.settings.api_base_url}/{path.lstrip('/')}"
        for attempt in range(self.settings.max_retries + 1):
            response = None
            try:
                response = self.http.request(method, url, params=query,
                    headers={"Authorization": f"Zoho-oauthtoken {token}", "Accept": "application/json"})
                if response.status_code == 401 and attempt == 0:
                    token = self._refresh_access_token()
                    continue
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < self.settings.max_retries:
                        self._sleep(self._retry_delay(response, attempt))
                        continue
                if response.status_code == 404:
                    raise ZohoAPIError("Record not found", 404)
                if response.status_code in (401, 403):
                    raise ZohoAPIError("Zoho authentication or permission error; check OAuth scopes and organization access", response.status_code)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict) and payload.get("code", 0) not in (0, "0", None):
                    # Zoho often returns application errors with HTTP 200.
                    raise ZohoAPIError(f"Zoho API returned application error code {payload.get('code')}")
                return payload
            except ZohoAPIError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < self.settings.max_retries:
                    self._sleep(self._retry_delay(None, attempt))
                    continue
                raise ZohoAPIError("Zoho request failed after retries due to a network or timeout error") from exc
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status >= 500 and attempt < self.settings.max_retries:
                    self._sleep(self._retry_delay(exc.response, attempt))
                    continue
                raise ZohoAPIError(f"Zoho API request failed with HTTP {status}", status) from exc
            except ValueError as exc:
                raise ZohoAPIError("Zoho API returned an invalid JSON response") from exc
        raise ZohoAPIError("Zoho request failed after retries")

    def list_items(self, page: int = 1, per_page: int = 20, search_text: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if search_text:
            params["search_text"] = search_text
        return self.request("GET", "items", params)

    def get_item(self, item_id: str) -> dict[str, Any]:
        return self.request("GET", f"items/{item_id}")

    def search_items(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        return self.list_items(page=page, per_page=per_page, search_text=query)

    def list_sales_orders(self, page: int = 1, per_page: int = 20, status: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status
        return self.request("GET", "salesorders", params)

    def get_sales_order(self, order_id: str) -> dict[str, Any]:
        return self.request("GET", f"salesorders/{order_id}")

    def close(self) -> None:
        self.http.close()
        self.token_http.close()
