import os
from datetime import datetime
from unittest.mock import patch

import pytest

from metpub.cli import main


def raise_system_exit(*args, **kwargs):
    code = args[0] if args else 0
    raise SystemExit(code)


@patch("metpub.cli.publish_hyper_extract")
@patch("metpub.cli.convert_json_to_hyper")
@patch("metpub.cli.config")
def test_cli_success_defaults(mock_config, mock_convert, mock_publish, tmp_path):
    # Setup mock config properties
    mock_config.TABLE_NAME = "Extract"
    mock_config.TOKEN_NAME = "test-token"
    mock_config.TOKEN_VALUE = "test-value"
    mock_config.SITE_ID = "test-site"
    mock_config.SERVER_URL = "https://server"
    mock_config.PROJECT_NAME = "test-project"

    current_year = datetime.now().year
    expected_json = f"{current_year}_govwifi_data.json"
    expected_hyper = f"{current_year}_govwifi_data.hyper"

    with patch.dict(os.environ, {}, clear=True):
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main([])
            mock_exit.assert_not_called()

        mock_convert.assert_called_once_with(
            json_path=expected_json,
            hyper_path=expected_hyper,
            table_name="Extract",
        )
        mock_publish.assert_called_once_with(
            hyper_path=expected_hyper,
            token_name="test-token",
            token_value="test-value",
            site_id="test-site",
            server_url="https://server",
            project_name="test-project",
            year=current_year,
            month=None,
        )


@patch("metpub.cli.publish_hyper_extract")
@patch("metpub.cli.convert_json_to_hyper")
@patch("metpub.cli.config")
def test_cli_success_with_args(mock_config, mock_convert, mock_publish, tmp_path):
    # Setup mock config properties
    mock_config.TABLE_NAME = "Extract"
    mock_config.TOKEN_NAME = "test-token"
    mock_config.TOKEN_VALUE = "test-value"
    mock_config.SITE_ID = "test-site"
    mock_config.SERVER_URL = "https://server"
    mock_config.PROJECT_NAME = "test-project"

    test_args = ["--year", "2025", "--month", "9"]

    with patch.dict(os.environ, {}, clear=True):
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main(test_args)
            mock_exit.assert_not_called()

        mock_convert.assert_called_once_with(
            json_path="2025_09_govwifi_data.json",
            hyper_path="2025_09_govwifi_data.hyper",
            table_name="Extract",
        )
        mock_publish.assert_called_once_with(
            hyper_path="2025_09_govwifi_data.hyper",
            token_name="test-token",
            token_value="test-value",
            site_id="test-site",
            server_url="https://server",
            project_name="test-project",
            year=2025,
            month=9,
        )


@patch("metpub.cli.publish_hyper_extract")
@patch("metpub.cli.convert_json_to_hyper")
@patch("metpub.cli.config")
def test_cli_arg_precedence_over_env(mock_config, mock_convert, mock_publish):
    mock_config.TABLE_NAME = "Extract"
    mock_config.TOKEN_NAME = "test-token"
    mock_config.TOKEN_VALUE = "test-value"
    mock_config.SITE_ID = "test-site"
    mock_config.SERVER_URL = "https://server"
    mock_config.PROJECT_NAME = "test-project"

    test_args = ["--year", "2027"]

    # Even though JSON_FILE_PATH is set in environment to "2026_govwifi_data.json",
    # specifying --year 2027 should override it to use "2027_govwifi_data.json"
    with patch.dict(
        os.environ,
        {
            "JSON_FILE_PATH": "2026_govwifi_data.json",
            "HYPER_FILE_PATH": "2026_govwifi_data.hyper",
        },
        clear=True,
    ):
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main(test_args)
            mock_exit.assert_not_called()

        mock_convert.assert_called_once_with(
            json_path="2027_govwifi_data.json",
            hyper_path="2027_govwifi_data.hyper",
            table_name="Extract",
        )


def test_cli_invalid_month(capsys):
    test_args = ["--month", "14"]
    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main(test_args)
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Error: Month must be between 1 and 12, got '14'" in captured.err


@patch("metpub.cli.convert_json_to_hyper")
def test_cli_exception_handling(mock_convert, capsys):
    mock_convert.side_effect = Exception("Failed file ingestion")

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Error: Failed file ingestion" in captured.err
