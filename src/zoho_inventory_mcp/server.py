from mcp.server.fastmcp import FastMCP

from .client import ZohoClient
from .config import Settings
from .tools import register_tools


def build_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or Settings.from_env()
    client = ZohoClient(settings)
    mcp = FastMCP("zoho-inventory-readonly")
    register_tools(mcp, client, settings)
    return mcp


def main() -> None:
    build_server().run(transport="stdio")

if __name__ == "__main__":
    main()
