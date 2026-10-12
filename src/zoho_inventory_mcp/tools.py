from .client import ZohoAPIError, ZohoClient
from .config import Settings


def _page(page: int, per_page: int, settings: Settings) -> tuple[int, int]:
    if page < 1:
        raise ValueError("page must be >= 1")
    if per_page < 1 or per_page > settings.max_per_page:
        raise ValueError(f"per_page must be between 1 and {settings.max_per_page}")
    return page, per_page


def register_tools(mcp, client: ZohoClient, settings: Settings) -> None:
    @mcp.tool()
    def list_items(page: int = 1, per_page: int = 20) -> dict:
        """List Zoho Inventory items/products. Read-only. Page size is capped by configuration."""
        page, per_page = _page(page, per_page, settings)
        try:
            return client.list_items(page, per_page)
        except ZohoAPIError as exc:
            return {"error": str(exc), "status_code": exc.status_code}

    @mcp.tool()
    def get_item(item_id: str) -> dict:
        """Get one inventory item by its Zoho item ID. Read-only."""
        if not item_id.strip().isdigit():
            raise ValueError("item_id must be a numeric Zoho ID")
        try:
            return client.get_item(item_id)
        except ZohoAPIError as exc:
            return {"error": str(exc), "status_code": exc.status_code}

    @mcp.tool()
    def search_items(query: str, page: int = 1, per_page: int = 20) -> dict:
        """Search inventory items by Zoho's supported search_text field. Read-only."""
        if not query.strip():
            raise ValueError("query must not be empty")
        page, per_page = _page(page, per_page, settings)
        try:
            return client.search_items(query.strip(), page, per_page)
        except ZohoAPIError as exc:
            return {"error": str(exc), "status_code": exc.status_code}

    @mcp.tool()
    def list_sales_orders(page: int = 1, per_page: int = 20, status: str | None = None) -> dict:
        """List sales orders, optionally filtered by a Zoho-supported status. Read-only."""
        page, per_page = _page(page, per_page, settings)
        try:
            return client.list_sales_orders(page, per_page, status)
        except ZohoAPIError as exc:
            return {"error": str(exc), "status_code": exc.status_code}

    @mcp.tool()
    def get_sales_order(order_id: str) -> dict:
        """Get one sales order by its Zoho sales-order ID. Read-only."""
        if not order_id.strip().isdigit():
            raise ValueError("order_id must be a numeric Zoho ID")
        try:
            return client.get_sales_order(order_id)
        except ZohoAPIError as exc:
            return {"error": str(exc), "status_code": exc.status_code}
