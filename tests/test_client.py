import httpx
import respx
import pytest
from zoho_inventory_mcp.client import ZohoAPIError, ZohoClient

TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"
ITEMS_URL = "https://www.zohoapis.in/inventory/v1/items"

def make_client(settings):
    return ZohoClient(settings, sleep=lambda _: None)

@respx.mock
def test_refresh_token_and_list_items(settings):
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(200, json={"access_token": "access"}))
    route = respx.get(ITEMS_URL).mock(return_value=httpx.Response(200, json={"code": 0, "items": [{"item_id": "9"}]}))
    result = make_client(settings).list_items(page=1, per_page=20)
    assert result["items"][0]["item_id"] == "9"
    assert route.calls[0].request.headers["Authorization"] == "Zoho-oauthtoken access"
    assert route.calls[0].request.url.params["organization_id"] == "123456"

@respx.mock
def test_retries_429(settings):
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(200, json={"access_token": "access"}))
    route = respx.get(ITEMS_URL)
    route.side_effect = [httpx.Response(429, headers={"Retry-After": "0"}), httpx.Response(200, json={"code": 0, "items": []})]
    result = make_client(settings).list_items()
    assert result["items"] == []
    assert route.call_count == 2

@respx.mock
def test_auth_error_is_safe(settings):
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(200, json={"access_token": "access"}))
    respx.get(ITEMS_URL).mock(return_value=httpx.Response(403, json={"message": "forbidden"}))
    with pytest.raises(ZohoAPIError, match="permission error"):
        make_client(settings).list_items()

@respx.mock
def test_not_found(settings):
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(200, json={"access_token": "access"}))
    respx.get(f"{ITEMS_URL}/999").mock(return_value=httpx.Response(404))
    with pytest.raises(ZohoAPIError, match="Record not found"):
        make_client(settings).get_item("999")
