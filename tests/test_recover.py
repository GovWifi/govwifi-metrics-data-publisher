import os
import urllib.error
from datetime import datetime
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from metpub.recover import main


def raise_system_exit(*args, **kwargs):
    code = args[0] if args else 0
    raise SystemExit(code)


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_success_defaults(mock_config, mock_urlopen, tmp_path):
    # Setup mock config
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    # Setup temporary directory for output file testing
    temp_dir = str(tmp_path)
    current_year = datetime.now().year
    expected_output = os.path.join(temp_dir, f"{current_year}_govwifi_data.json")

    # Use patch.dict to avoid config.JSON_FILE_PATH returning original default
    # since JSON_FILE_PATH env override will be detected.
    with patch.dict(os.environ, {"JSON_FILE_PATH": expected_output}, clear=True):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.read.side_effect = [b'{"recovered": true}', b""]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Execute
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main([])
            mock_exit.assert_not_called()

        # Verify
        mock_urlopen.assert_called_once()
        called_req = mock_urlopen.call_args[0][0]
        assert (
            called_req.full_url
            == f"https://api.example.com/v1/data/export?year={current_year}"
        )
        assert called_req.headers["Authorization"] == "Bearer test-api-key"

        with open(expected_output, "r") as f:
            assert f.read() == '{"recovered": true}'


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_success_with_args(mock_config, mock_urlopen, tmp_path):
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    mock_response = MagicMock()
    mock_response.read.side_effect = [b'{"recovered_month": true}', b""]
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Test CLI parameters: year and month
    test_args = ["--year", "2025", "--month", "6"]

    # We should run it inside the tmp_path directory to verify the adaptive
    # filename location
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Patch os.environ to be empty to prevent loading local .env file
        # values (which override output filename)
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
                main(test_args)
                mock_exit.assert_not_called()

        expected_filename = "2025_06_govwifi_data.json"
        assert os.path.exists(expected_filename)
        with open(expected_filename, "r") as f:
            assert f.read() == '{"recovered_month": true}'

        mock_urlopen.assert_called_once()
        called_req = mock_urlopen.call_args[0][0]
        assert called_req.full_url == (
            "https://api.example.com/v1/data/export?year=2025&month=6"
        )
    finally:
        os.chdir(current_dir)


@patch("metpub.recover.config")
def test_recover_invalid_month(mock_config, capsys):
    test_args = ["--month", "13"]
    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main(test_args)
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Error: Month must be between 1 and 12, got '13'" in captured.err


@patch("metpub.recover.config")
def test_recover_missing_config(mock_config, capsys):
    # Setup METRICS_API_URL to raise ValueError using PropertyMock
    type(mock_config).METRICS_API_URL = PropertyMock(
        side_effect=ValueError("Missing required environment variable: METRICS_API_URL")
    )

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert (
            "Configuration Error: Missing required environment variable: "
            "METRICS_API_URL" in captured.err
        )


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_http_error(mock_config, mock_urlopen, capsys):
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    # Setup urllib to raise HTTPError
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="https://api.example.com",
        code=403,
        msg="Forbidden",
        hdrs=None,
        fp=None,
    )

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "HTTP Error 403: Forbidden" in captured.err


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_url_error(mock_config, mock_urlopen, capsys):
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Network Error: Connection refused" in captured.err


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_general_exception(mock_config, mock_urlopen, capsys):
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    mock_urlopen.side_effect = Exception("Fatal OS Exception")

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Error: Fatal OS Exception" in captured.err


@patch("metpub.recover.urllib.request.urlopen")
@patch("metpub.recover.config")
def test_recover_arg_precedence_over_env(mock_config, mock_urlopen, tmp_path):
    mock_config.METRICS_API_URL = "https://api.example.com"
    mock_config.METRICS_API_KEY = "test-api-key"

    mock_response = MagicMock()
    mock_response.read.side_effect = [b'{"recovered": true}', b""]
    mock_urlopen.return_value.__enter__.return_value = mock_response

    test_args = ["--year", "2027"]

    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Running with --year 2027 should override it and save to
        # "2027_govwifi_data.json".
        with patch.dict(
            os.environ,
            {
                "JSON_FILE_PATH": "2026_govwifi_data.json",
            },
            clear=True,
        ):
            with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
                main(test_args)
                mock_exit.assert_not_called()

        expected_filename = "2027_govwifi_data.json"
        assert os.path.exists(expected_filename)
        with open(expected_filename, "r") as f:
            assert f.read() == '{"recovered": true}'
    finally:
        os.chdir(current_dir)
