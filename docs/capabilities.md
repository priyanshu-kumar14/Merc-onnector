# Zoho Inventory MCP Connector — Capabilities and Limitations

## Purpose
Expose read-only Zoho Inventory items and sales orders to an MCP-compatible AI agent using Zoho OAuth 2.0 refresh-token authentication.

## Supported tools
- `list_items`: list inventory items with pagination.
- `get_item`: retrieve an item by numeric Zoho item ID.
- `search_items`: search items using Zoho's `search_text` parameter.
- `list_sales_orders`: list sales orders with pagination and optional status filter.
- `get_sales_order`: retrieve a sales order by numeric ID.

## Restrictions
- Does not create, update, or delete items, sales orders, contacts, or organizations.
- Does not adjust stock, confirm/ship orders, issue invoices, or process payments.
- Only sees data accessible to the OAuth-authorized Zoho user and organization.
- Search and filter behavior is limited to the parameters supported by the Zoho Inventory API and the account's edition.
- Inventory availability may change after the API response is returned.

## Security
- Keep OAuth client secret and refresh token in `.env` or a secret manager; never commit them.
- Use the narrowest OAuth scopes required for item and sales-order read access.
- Use HTTPS and a dedicated Zoho integration identity where possible.
- Never log access tokens, refresh tokens, client secrets, or full sensitive customer payloads.
- Tool methods are read-only; do not add write endpoints without explicit authorization and additional safety controls.

## Reliability
- Adds `organization_id` to Inventory API calls.
- Uses bounded retries for network errors, HTTP 5xx, and HTTP 429; honors numeric `Retry-After` values up to 30 seconds.
- Validates pagination and caps `per_page`.
- Returns safe error messages for authentication, permission, missing-record, and upstream failures.

## Operational limitations
- The project defaults to Zoho's India data center (`accounts.zoho.in`, `www.zohoapis.in`). Set both URL variables to the matching Zoho data-center domains for your account.
- OAuth setup and grant creation must be completed in Zoho API Console before running against a real account.
- Automated tests use mocked API responses; live integration must be separately verified in a Zoho Inventory organization.
