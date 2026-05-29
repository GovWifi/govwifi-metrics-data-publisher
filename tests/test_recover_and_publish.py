import os
from datetime import datetime
from unittest.mock import patch

import pytest

from metpub.recover_and_publish import main


def raise_system_exit(*args, **kwargs):
    code = args[0] if args else 0
    raise SystemExit(code)


@patch("metpub.recover_and_publish.publish_metrics")
@patch("metpub.recover_and_publish.recover_metrics")
@patch("metpub.recover_and_publish.config")
def test_sync_success_defaults(mock_config, mock_recover, mock_publish):
    # Setup mock config
    mock_config.TABLE_NAME = "Extract"
    mock_recover.return_value = "2026_govwifi_data.json"

    current_year = datetime.now().year

    with patch.dict(os.environ, {}, clear=True):
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main([])
            mock_exit.assert_not_called()

    # Verify recover_metrics and publish_metrics were called with the correct defaults
    mock_recover.assert_called_once_with(
        year=current_year,
        month=None,
        output_path=f"{current_year}_govwifi_data.json",
    )
    mock_publish.assert_called_once_with(
        json_path="2026_govwifi_data.json",
        hyper_path=f"{current_year}_govwifi_data.hyper",
        table_name="Extract",
        year=current_year,
        month=None,
    )


@patch("metpub.recover_and_publish.publish_metrics")
@patch("metpub.recover_and_publish.recover_metrics")
@patch("metpub.recover_and_publish.config")
def test_sync_success_with_args(mock_config, mock_recover, mock_publish):
    mock_config.TABLE_NAME = "Extract"
    mock_recover.return_value = "2025_06_govwifi_data.json"

    test_args = ["--year", "2025", "--month", "6"]

    with patch.dict(os.environ, {}, clear=True):
        with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
            main(test_args)
            mock_exit.assert_not_called()

    # Verify recover_metrics and publish_metrics were called with specified arguments
    mock_recover.assert_called_once_with(
        year=2025,
        month=6,
        output_path="2025_06_govwifi_data.json",
    )
    mock_publish.assert_called_once_with(
        json_path="2025_06_govwifi_data.json",
        hyper_path="2025_06_govwifi_data.hyper",
        table_name="Extract",
        year=2025,
        month=6,
    )


def test_sync_invalid_month(capsys):
    test_args = ["--month", "13"]

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main(test_args)
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Error: Month must be between 1 and 12, got '13'" in captured.err


@patch("metpub.recover_and_publish.recover_metrics")
def test_sync_recovery_fails(mock_recover, capsys):
    mock_recover.side_effect = Exception("API Server Unavailable")

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Recovery failed: API Server Unavailable" in captured.err


@patch("metpub.recover_and_publish.publish_metrics")
@patch("metpub.recover_and_publish.recover_metrics")
def test_sync_publish_fails(mock_recover, mock_publish, capsys):
    mock_recover.return_value = "2026_govwifi_data.json"
    mock_publish.side_effect = Exception("Tableau Credentials Expired")

    with patch("sys.exit", side_effect=raise_system_exit) as mock_exit:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1
        mock_exit.assert_called_once_with(1)

        captured = capsys.readouterr()
        assert "Publish failed: Tableau Credentials Expired" in captured.err
