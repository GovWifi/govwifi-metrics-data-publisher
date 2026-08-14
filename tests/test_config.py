import os
from datetime import datetime
from unittest.mock import patch

import pytest

from metpub.config import Config


def test_config_default_paths():
    current_year = datetime.now().year
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.JSON_FILE_PATH == f"{current_year}_govwifi_data.json"
        assert config.HYPER_FILE_PATH == f"{current_year}_govwifi_data.hyper"
        assert config.TABLE_NAME == "Extract"


def test_config_overrides():
    with patch.dict(
        os.environ,
        {
            "JSON_FILE_PATH": "custom.json",
            "HYPER_FILE_PATH": "custom.hyper",
            "TABLE_NAME": "CustomTable",
        },
        clear=True,
    ):
        config = Config()
        assert config.JSON_FILE_PATH == "custom.json"
        assert config.HYPER_FILE_PATH == "custom.hyper"
        assert config.TABLE_NAME == "CustomTable"


def test_config_required_missing():
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        with pytest.raises(
            ValueError,
            match="Missing required environment variable: TOKEN_NAME",
        ):
            _ = config.TOKEN_NAME

        with pytest.raises(
            ValueError,
            match="Missing required environment variable: METRICS_API_URL",
        ):
            _ = config.METRICS_API_URL


def test_config_required_present():
    with patch.dict(
        os.environ,
        {
            "TOKEN_NAME": "my-token",
            "METRICS_API_URL": "http://api.local",
        },
        clear=True,
    ):
        config = Config()
        assert config.TOKEN_NAME == "my-token"
        assert config.METRICS_API_URL == "http://api.local"


def test_config_environment():
    # 1. Default (when not present)
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.ENVIRONMENT == "Development"

    # 2. Custom value (e.g. production -> Production)
    with patch.dict(os.environ, {"ENVIRONMENT_NAME": "production"}, clear=True):
        config = Config()
        assert config.ENVIRONMENT == "Production"

    # 3. Another custom value (e.g. staging -> Staging)
    with patch.dict(os.environ, {"ENVIRONMENT_NAME": "staging"}, clear=True):
        config = Config()
        assert config.ENVIRONMENT == "Staging"

    # 4. A generic custom environment name (e.g. preview -> Preview)
    with patch.dict(os.environ, {"ENVIRONMENT_NAME": "preview"}, clear=True):
        config = Config()
        assert config.ENVIRONMENT == "Preview"

    # 5. Empty value -> falls back to Development
    with patch.dict(os.environ, {"ENVIRONMENT_NAME": ""}, clear=True):
        config = Config()
        assert config.ENVIRONMENT == "Development"
