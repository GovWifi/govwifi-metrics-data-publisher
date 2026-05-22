import pandas as pd
import pantab

VALUE_ALIASES = {
    "monthly-rolling-window-total-active-users": "Active Users",
    "monthly-rolling-window-total-roaming-users": "Roaming Users",
    "month-to-date-total-active-users": "Active Users (MTD)",
    "month-to-date-total-roaming-users": "Roaming Users (MTD)",
}


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply aliases to the 'name' column of the dataframe."""
    df = df.copy()
    if "name" in df.columns:
        df["name"] = df["name"].replace(VALUE_ALIASES)
    return df


def convert_json_to_hyper(json_path: str, hyper_path: str, table_name: str) -> None:
    """Reads JSON data, transforms it, and saves as a Tableau Hyper Extract."""
    print(f"Reading JSON from {json_path}...")
    try:
        df = pd.read_json(json_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read JSON file {json_path}: {e}")

    df = transform_dataframe(df)

    print(f"Converting DataFrame to {hyper_path}...")
    try:
        pantab.frame_to_hyper(df, hyper_path, table=table_name)
    except Exception as e:
        raise RuntimeError(f"Failed to create hyper extract: {e}")
