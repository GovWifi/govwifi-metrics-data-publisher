import argparse
import os
import sys
from datetime import datetime

from metpub.cli import publish_metrics
from metpub.config import config
from metpub.recover import recover_metrics


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="GovWifi Metrics Data Recovery and Publisher"
    )

    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="The year to recover and publish data for (default: current year)",
    )

    parser.add_argument(
        "--month",
        type=int,
        default=None,
        help="Optional month (1-12) to recover and publish data for",
    )

    return parser.parse_args(args)


def main(args=None) -> None:
    print("Starting GovWifi Metrics Data Recovery and Publisher...")

    # Step 1: Parse arguments and resolve values
    parsed_args = parse_args(args)

    year = parsed_args.year
    if year is None:
        year = int(os.environ.get("RECOVER_YEAR", datetime.now().year))

    month = parsed_args.month
    if month is None:
        month_env = os.environ.get("RECOVER_MONTH")
        month = int(month_env) if month_env else None

    # Step 2: Input validation
    if month is not None and not (1 <= month <= 12):
        print(
            f"Error: Month must be between 1 and 12, got '{month}'",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 3: Determine JSON and Hyper paths
    is_cli_override = (parsed_args.year is not None) or (parsed_args.month is not None)

    if is_cli_override:
        if month is not None:
            json_path = f"{year}_{month:02d}_govwifi_data.json"
            hyper_path = f"{year}_{month:02d}_govwifi_data.hyper"
        else:
            json_path = f"{year}_govwifi_data.json"
            hyper_path = f"{year}_govwifi_data.hyper"
    else:
        env_json_path = os.environ.get("JSON_FILE_PATH")
        if env_json_path:
            json_path = env_json_path
        else:
            if month is not None:
                json_path = f"{year}_{month:02d}_govwifi_data.json"
            else:
                json_path = f"{year}_govwifi_data.json"

        env_hyper_path = os.environ.get("HYPER_FILE_PATH")
        if env_hyper_path:
            hyper_path = env_hyper_path
        else:
            if month is not None:
                hyper_path = f"{year}_{month:02d}_govwifi_data.hyper"
            else:
                hyper_path = f"{year}_govwifi_data.hyper"

    # Step 4: Run recovery
    print(f"\n--- Phase 1: Recovering metrics data for year={year}, month={month} ---")
    try:
        resolved_json_path = recover_metrics(
            year=year,
            month=month,
            output_path=json_path,
        )
    except Exception as e:
        print(f"Recovery failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 5: Convert and publish
    print(f"\n--- Phase 2: Publishing data from {resolved_json_path} ---")
    try:
        publish_metrics(
            json_path=resolved_json_path,
            hyper_path=hyper_path,
            table_name=config.TABLE_NAME,
            year=year,
            month=month,
        )
        print("\n--- Synchronization Successful! ---")
    except Exception as e:
        print(f"Publish failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
