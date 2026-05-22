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
