import pandas as pd

from metpub.converter import transform_dataframe


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
