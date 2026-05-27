from unittest.mock import MagicMock, patch

import pytest

from metpub.publisher import publish_hyper_extract


@patch("metpub.publisher.TSC")
def test_publish_hyper_extract_success(mock_tsc):
    # Setup mocks
    mock_server = MagicMock()
    mock_tsc.Server.return_value = mock_server

    # Mock projects
    mock_project = MagicMock()
    mock_project.id = "proj-123"
    mock_server.projects.get.return_value = ([mock_project], None)

    # Mock publish
    mock_published_ds = MagicMock()
    mock_published_ds.id = "ds-456"
    mock_server.datasources.publish.return_value = mock_published_ds

    # Call the function
    publish_hyper_extract(
        hyper_path="test.hyper",
        token_name="token_name",
        token_value="token_value",
        site_id="site_id",
        server_url="http://test.server",
        project_name="Test Project",
        year=2026,
        month=5,
    )

    # Assertions
    mock_tsc.PersonalAccessTokenAuth.assert_called_once_with(
        "token_name", "token_value", "site_id"
    )
    mock_tsc.Server.assert_called_once_with(
        "http://test.server", use_server_version=True
    )
    mock_server.auth.sign_in.assert_called_once()
    mock_server.projects.get.assert_called_once()
    mock_tsc.DatasourceItem.assert_called_once_with(
        "proj-123", name="2026-05 GovWifi Data"
    )
    mock_server.datasources.publish.assert_called_once()


@patch("metpub.publisher.TSC")
def test_publish_hyper_extract_success_no_month(mock_tsc):
    # Setup mocks
    mock_server = MagicMock()
    mock_tsc.Server.return_value = mock_server

    # Mock projects
    mock_project = MagicMock()
    mock_project.id = "proj-123"
    mock_server.projects.get.return_value = ([mock_project], None)

    # Mock publish
    mock_published_ds = MagicMock()
    mock_published_ds.id = "ds-456"
    mock_server.datasources.publish.return_value = mock_published_ds

    # Call the function with no month
    publish_hyper_extract(
        hyper_path="test.hyper",
        token_name="token_name",
        token_value="token_value",
        site_id="site_id",
        server_url="http://test.server",
        project_name="Test Project",
        year=2026,
    )

    # Assertions
    mock_tsc.DatasourceItem.assert_called_once_with(
        "proj-123", name="2026 GovWifi Data"
    )
    mock_server.datasources.publish.assert_called_once()


@patch("metpub.publisher.TSC")
def test_publish_hyper_extract_project_not_found(mock_tsc):
    # Setup mocks
    mock_server = MagicMock()
    mock_tsc.Server.return_value = mock_server

    # Mock projects to return empty list
    mock_server.projects.get.return_value = ([], None)

    # Expect ValueError
    with pytest.raises(ValueError, match="Project 'Test Project' not found."):
        publish_hyper_extract(
            hyper_path="test.hyper",
            token_name="token_name",
            token_value="token_value",
            site_id="site_id",
            server_url="http://test.server",
            project_name="Test Project",
            year=2026,
            month=5,
        )
