# Zoho Inventory MCP Connector (read-only)

A Python MCP server that exposes read-only Zoho Inventory item and sales-order operations to compatible AI agents.

## Features
- OAuth 2.0 refresh-token flow (no hard-coded access token)
- List/search/get items and list/get sales orders
- Organization-scoped API requests
- Pagination validation and configurable page cap
- Bounded retry/backoff for HTTP 429, HTTP 5xx and transient network failures
- Safe error messages and mocked tests
- MCP stdio transport

## Requirements
- Python 3.11+
- Zoho Inventory organization and OAuth credentials with read access to items and sales orders
- Internet access for live API calls

## Setup on macOS

```bash
cd zoho-inventory-mcp-connector
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
cp .env.example .env
open -e .env
```

Fill in `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, and `ZOHO_ORGANIZATION_ID`. Defaults target the India data center. Change `ZOHO_ACCOUNTS_URL` and `ZOHO_API_BASE_URL` together for your account's Zoho data center.

## OAuth setup overview
1. Open the Zoho API Console: https://api-console.zoho.in/ (India data center; use the matching regional console for other regions).
2. Register an appropriate server-based application and note its client ID and client secret.
3. Create a refresh token using Zoho's OAuth flow with only the scopes required for reading items and sales orders. Scope names can vary by Zoho Inventory API version; consult the current API documentation before generating the grant.
4. Find the organization ID in Zoho Inventory or through the organizations endpoint, using the same authorized account.
5. Store credentials only in `.env` or a secret manager. Never commit `.env`.

Zoho OAuth docs: https://www.zoho.com/accounts/protocol/oauth.html
Zoho Inventory API docs: https://www.zoho.com/inventory/api/v1/

## Run tests (no Zoho account required)

```bash
pytest -v
```

The tests mock OAuth and API HTTP responses. They verify token use, organization scoping, 429 retry, safe permission errors, not-found handling, and pagination validation. They do not prove live-account access.

## Start MCP server

```bash
zoho-inventory-mcp
```

Alternative:

```bash
python -m zoho_inventory_mcp.server
```

This uses stdio transport. A compatible MCP host must launch it as a subprocess; it is not a browser-based web server. Use MCP Inspector for manual testing if needed.

## Tools
- `list_items(page=1, per_page=20)`
- `get_item(item_id)`
- `search_items(query, page=1, per_page=20)`
- `list_sales_orders(page=1, per_page=20, status=None)`
- `get_sales_order(order_id)`

Schemas are in `docs/tool-specification.json`; capabilities and restrictions are in `docs/capabilities.md`.

## Rate limits and errors
- Numeric `Retry-After` is honored up to 30 seconds; otherwise bounded exponential backoff with jitter is used.
- Network/timeout, HTTP 429 and 5xx responses are retried up to `ZOHO_MAX_RETRIES`.
- 401/403 errors are reported without exposing credentials; 404 returns a not-found error.
- `per_page` is limited by `ZOHO_MAX_PER_PAGE` (default 100).

## Security boundaries
The connector is read-only. It does not create/update/delete inventory items or sales orders. Keep OAuth secrets private, use minimal scopes, and review agent output before acting on any business decision.
