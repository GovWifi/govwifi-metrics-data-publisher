import os

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    def __init__(self):
        # Optional overrides
        self.JSON_FILE_PATH = os.environ.get("JSON_FILE_PATH", "2026_govwifi_data.json")
        self.HYPER_FILE_PATH = os.environ.get(
            "HYPER_FILE_PATH", "2026_govwifi_data.hyper"
        )
        # Required Tableau Cloud configurations
        self.TOKEN_NAME = self._get_required("TOKEN_NAME")
        self.TOKEN_VALUE = self._get_required("TOKEN_VALUE")
        self.SITE_ID = self._get_required("SITE_ID")
        self.SERVER_URL = self._get_required("SERVER_URL")
        self.PROJECT_NAME = self._get_required("PROJECT_NAME")
        self.DATASOURCE_NAME = self._get_required("DATASOURCE_NAME")

        # Optional: table name for the Hyper file (defaults to "Extract")
        #
        # Tableau has a standard convention for single-table extracts: it
        # expects the table to be named Extract. When you use this default name,
        # Tableau maps it perfectly on every overwrite without regenerating the
        # logical metadata, keeping your auto-generated fields stable.
        #
        self.TABLE_NAME = os.environ.get("TABLE_NAME", "Extract")

    def _get_required(self, key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value


# Singleton instance to be imported across the app
config = Config()
