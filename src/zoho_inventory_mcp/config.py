from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    accounts_url: str
    api_base_url: str
    client_id: str
    client_secret: str
    refresh_token: str
    organization_id: str
    timeout_seconds: float = 20.0
    max_retries: int = 3
    max_per_page: int = 100

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        required = {
            "ZOHO_CLIENT_ID": os.getenv("ZOHO_CLIENT_ID", "").strip(),
            "ZOHO_CLIENT_SECRET": os.getenv("ZOHO_CLIENT_SECRET", "").strip(),
            "ZOHO_REFRESH_TOKEN": os.getenv("ZOHO_REFRESH_TOKEN", "").strip(),
            "ZOHO_ORGANIZATION_ID": os.getenv("ZOHO_ORGANIZATION_ID", "").strip(),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))
        timeout = float(os.getenv("ZOHO_TIMEOUT_SECONDS", "20"))
        retries = int(os.getenv("ZOHO_MAX_RETRIES", "3"))
        max_page = int(os.getenv("ZOHO_MAX_PER_PAGE", "100"))
        if timeout <= 0 or retries < 0 or not 1 <= max_page <= 200:
            raise ValueError("Invalid timeout, retry count, or max page size")
        return cls(
            accounts_url=os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in").rstrip("/"),
            api_base_url=os.getenv("ZOHO_API_BASE_URL", "https://www.zohoapis.in/inventory/v1").rstrip("/"),
            client_id=required["ZOHO_CLIENT_ID"],
            client_secret=required["ZOHO_CLIENT_SECRET"],
            refresh_token=required["ZOHO_REFRESH_TOKEN"],
            organization_id=required["ZOHO_ORGANIZATION_ID"],
            timeout_seconds=timeout,
            max_retries=retries,
            max_per_page=max_page,
        )
