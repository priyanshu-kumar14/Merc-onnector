import pytest
from zoho_inventory_mcp.config import Settings

@pytest.fixture
def settings():
    return Settings(
        accounts_url="https://accounts.zoho.in",
        api_base_url="https://www.zohoapis.in/inventory/v1",
        client_id="client-id", client_secret="client-secret", refresh_token="refresh-token",
        organization_id="123456", timeout_seconds=2, max_retries=2, max_per_page=100,
    )
