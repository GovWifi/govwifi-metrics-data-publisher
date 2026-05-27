import argparse
import os
import sys
from datetime import datetime

from metpub.config import config
from metpub.converter import convert_json_to_hyper
from metpub.publisher import publish_hyper_extract


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="GovWifi Metrics Data Publisher")

    # Use None as default to identify if user explicitly passed arguments
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="The year of the data to publish (default: current calendar year)",
    )

    parser.add_argument(
        "--month",
        type=int,
        default=None,
        help="Optional month (1-12) of the data to publish",
    )

    return parser.parse_args(args)


def publish_metrics(
    json_path: str,
    hyper_path: str,
    table_name: str,
    year: int,
    month: int | None = None,
) -> None:
    """Converts a JSON metrics file to a Hyper extract and publishes it to
    Tableau Cloud.
    """
    convert_json_to_hyper(
        json_path=json_path,
        hyper_path=hyper_path,
        table_name=table_name,
    )

    publish_hyper_extract(
        hyper_path=hyper_path,
        token_name=config.TOKEN_NAME,
        token_value=config.TOKEN_VALUE,
        site_id=config.SITE_ID,
        server_url=config.SERVER_URL,
        project_name=config.PROJECT_NAME,
        year=year,
        month=month,
    )


def main(args=None) -> None:
    print("Starting GovWifi Metrics Data Publisher...")

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

    # Step 3: Determine input and output paths
    # If the user explicitly customized the year or month on the command line,
    # we prioritize the dynamic paths derived from their selection.
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

    try:
        publish_metrics(
            json_path=json_path,
            hyper_path=hyper_path,
            table_name=config.TABLE_NAME,
            year=year,
            month=month,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
