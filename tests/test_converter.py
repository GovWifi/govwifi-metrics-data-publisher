import json

import pandas as pd
import pantab
import pytest

from metpub.converter import convert_json_to_hyper, transform_dataframe


def test_transform_dataframe_applies_aliases():
    # Setup test data
    data = {
        "name": [
            "monthly-rolling-window-total-active-users",
            "unknown-metric",
            "month-to-date-total-roaming-users",
        ],
        "value": [100, 200, 300],
    }
    df = pd.DataFrame(data)

    # Transform
    transformed_df = transform_dataframe(df)

    # Verify
    expected_names = [
        "Active Users",
        "unknown-metric",  # Should remain unchanged
        "Roaming Users (MTD)",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [100, 200, 300]


def test_transform_dataframe_missing_name_col():
    # Should safely return dataframe if 'name' is missing
    df = pd.DataFrame({"other_col": [1, 2, 3]})
    transformed_df = transform_dataframe(df)

    assert list(transformed_df.columns) == ["other_col"]
    assert len(transformed_df) == 3


def test_transform_dataframe_applies_account_health_aliases():
    # Setup test data
    data = {
        "name": [
            "account-health-organisation-count",
            "account-health-orgs-with-less-than-two-admins-count",
            "account-health-orgs-with-dormant-admins-count",
            "account-health-orgs-have-no-active-admins-count",
            "account-health-orgs-with-no-signed-mou-count",
            "account-health-orgs-with-no-physical-address-for-ip-count",
        ],
        "value": [10, 20, 30, 40, 50, 60],
    }
    df = pd.DataFrame(data)

    # Transform
    transformed_df = transform_dataframe(df)

    # Verify
    expected_names = [
        "Total Organisations",
        "Less than Two Admins",
        "With Dormant Admins",
        "No Active Admins",
        "No Signed MoU",
        "IPs without physical addresses",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [10, 20, 30, 40, 50, 60]


def test_transform_dataframe_applies_tls_unique_users_aliases():
    data = {
        "name": [
            "service-report-active-tls-user-rolling-count",
            "service-report-active-tls-user-mtd-count",
        ],
        "value": [47073, 12500],
    }
    df = pd.DataFrame(data)

    transformed_df = transform_dataframe(df)

    expected_names = [
        "TLS Unique Users",
        "TLS Unique Users (MTD)",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [47073, 12500]


def test_transform_dataframe_applies_peap_unique_users_aliases():
    data = {
        "name": [
            "service-report-peap-unique-users-rolling-count",
            "service-report-peap-unique-users-mtd-count",
        ],
        "value": [47073, 12500],
    }
    df = pd.DataFrame(data)

    transformed_df = transform_dataframe(df)

    expected_names = [
        "PEAP Unique Users",
        "PEAP Unique Users (MTD)",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [47073, 12500]


def test_transform_dataframe_applies_organisations_added_aliases():
    data = {
        "name": [
            "service-report-organisations-addeded-rolling-count",
            "service-report-organisations-addeded-mtd-count",
        ],
        "value": [47073, 12500],
    }
    df = pd.DataFrame(data)

    transformed_df = transform_dataframe(df)

    expected_names = [
        "Organisations Added",
        "Organisations Added (MTD)",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [47073, 12500]


def test_transform_dataframe_applies_locations_added_aliases():
    data = {
        "name": [
            "service-report-locations-added-rolling-count",
            "service-report-locations-added-mtd-count",
        ],
        "value": [47073, 12500],
    }
    df = pd.DataFrame(data)

    transformed_df = transform_dataframe(df)

    expected_names = [
        "Locations Added",
        "Locations Added (MTD)",
    ]

    assert list(transformed_df["name"]) == expected_names
    assert list(transformed_df["value"]) == [47073, 12500]


def test_transform_dataframe_preserves_zero_values():
    """Verify transform_dataframe retains explicit 0 and 0.0 values across aliases."""
    data = {
        "name": [
            "service-report-organisations-addeded-mtd-count",
            "service-report-locations-added-mtd-count",
            "account-health-orgs-with-no-physical-address-for-ip-count",
        ],
        "value": [0, 0.0, 0],
    }
    df = pd.DataFrame(data)
    transformed_df = transform_dataframe(df)

    assert list(transformed_df["name"]) == [
        "Organisations Added (MTD)",
        "Locations Added (MTD)",
        "IPs without physical addresses",
    ]
    assert list(transformed_df["value"]) == [0, 0.0, 0]


def test_convert_json_to_hyper_preserves_zero_values_in_extract(tmp_path):
    """End-to-end test: writes JSON mimicking Metrics API export containing 0 values,
    converts to Hyper extract, and verifies with pantab that 0 values are present in
    the table.
    """
    mock_api_payload = [
        {
            "id": 101,
            "datetime": "2026-10-06 00:00:00 +0000",
            "name": "service-report-organisations-addeded-mtd-count",
            "value": 0.0,
        },
        {
            "id": 102,
            "datetime": "2026-10-06 00:00:00 +0000",
            "name": "service-report-locations-added-mtd-count",
            "value": 0.0,
        },
        {
            "id": 103,
            "datetime": "2026-10-06 00:00:00 +0000",
            "name": "account-health-orgs-with-no-physical-address-for-ip-count",
            "value": 0,
        },
        {
            "id": 104,
            "datetime": "2026-10-06 00:00:00 +0000",
            "name": "monthly-rolling-window-total-active-users",
            "value": 985000,
        },
    ]

    json_file = tmp_path / "mock_metrics_export.json"
    hyper_file = tmp_path / "test_extract.hyper"
    json_file.write_text(json.dumps(mock_api_payload))

    convert_json_to_hyper(
        json_path=str(json_file),
        hyper_path=str(hyper_file),
        table_name="Extract",
    )

    result_dfs = pantab.frames_from_hyper(str(hyper_file))
    df = result_dfs[("public", "Extract")]

    assert len(df) == 4
    zeros_df = df[df["value"] == 0]
    assert len(zeros_df) == 3
    assert set(zeros_df["name"]) == {
        "Organisations Added (MTD)",
        "Locations Added (MTD)",
        "IPs without physical addresses",
    }


def test_convert_json_to_hyper_invalid_json_raises_runtime_error(tmp_path):
    """Verify convert_json_to_hyper raises RuntimeError on corrupted JSON."""
    bad_json = tmp_path / "invalid.json"
    bad_json.write_text("not-valid-json")
    hyper_file = tmp_path / "out.hyper"

    with pytest.raises(RuntimeError, match="Failed to read JSON file"):
        convert_json_to_hyper(str(bad_json), str(hyper_file), "Extract")


def test_convert_json_to_hyper_failure_raises_runtime_error(monkeypatch, tmp_path):
    """Verify convert_json_to_hyper wraps pantab exceptions in RuntimeError."""
    valid_json = tmp_path / "valid.json"
    valid_json.write_text(json.dumps([{"name": "test", "value": 0}]))
    hyper_file = tmp_path / "out.hyper"

    def mock_frame_to_hyper(*args, **kwargs):
        raise ValueError("Pantab conversion error")

    monkeypatch.setattr(pantab, "frame_to_hyper", mock_frame_to_hyper)

    with pytest.raises(RuntimeError, match="Failed to create hyper extract"):
        convert_json_to_hyper(str(valid_json), str(hyper_file), "Extract")
