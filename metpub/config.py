import os
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:

    @property
    def JSON_FILE_PATH(self) -> str:
        current_year = datetime.now().year
        return os.environ.get("JSON_FILE_PATH", f"{current_year}_govwifi_data.json")

    @property
    def HYPER_FILE_PATH(self) -> str:
        current_year = datetime.now().year
        return os.environ.get("HYPER_FILE_PATH", f"{current_year}_govwifi_data.hyper")

    @property
    def TABLE_NAME(self) -> str:
        return os.environ.get("TABLE_NAME", "Extract")

    @property
    def TOKEN_NAME(self) -> str:
        return self._get_required("TOKEN_NAME")

    @property
    def TOKEN_VALUE(self) -> str:
        return self._get_required("TOKEN_VALUE")

    @property
    def SITE_ID(self) -> str:
        return self._get_required("SITE_ID")

    @property
    def SERVER_URL(self) -> str:
        return self._get_required("SERVER_URL")

    @property
    def PROJECT_NAME(self) -> str:
        return self._get_required("PROJECT_NAME")


    @property
    def METRICS_API_URL(self) -> str:
        return self._get_required("METRICS_API_URL")

    @property
    def METRICS_API_KEY(self) -> str:
        return self._get_required("METRICS_API_KEY")

    def _get_required(self, key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value


# Singleton instance to be imported across the app
config = Config()
