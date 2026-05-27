import argparse
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

from metpub.config import config


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="GovWifi Metrics Data Recovery")

    # Use None as default to identify if user explicitly passed arguments
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="The year to recover data for (default: current calendar year)",
    )

    parser.add_argument(
        "--month",
        type=int,
        default=None,
        help="Optional month (1-12) to recover data for",
    )

    return parser.parse_args(args)


def recover_metrics(
    year: int, month: int | None = None, output_path: str | None = None
) -> str:
    """Performs the recovery request and streams the download to the output path.

    Returns the resolved output path.
    """
    # Load and validate API configurations
    try:
        api_url = config.METRICS_API_URL
        api_key = config.METRICS_API_KEY
    except ValueError as e:
        raise ValueError(f"Configuration Error: {e}")

    # Determine output path if not provided
    if not output_path:
        env_json_path = os.environ.get("JSON_FILE_PATH")
        if env_json_path:
            output_path = env_json_path
        else:
            if month is not None:
                output_path = f"{year}_{month:02d}_govwifi_data.json"
            else:
                output_path = f"{year}_govwifi_data.json"

    # Construct endpoint URL
    base_url = api_url.rstrip("/")
    recover_url = f"{base_url}/v1/data/export?year={year}"
    if month is not None:
        recover_url += f"&month={month}"

    print(f"Requesting recovery data from: {recover_url}")
    print(f"Streaming output to: {output_path}")

    # Perform recovery and stream file download
    req = urllib.request.Request(recover_url)
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req) as response:
            with open(output_path, "wb") as f:
                while chunk := response.read(8192):
                    f.write(chunk)

        print(f"Success! Metrics data recovered and saved to {output_path}")
        return output_path

    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network Error: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def main(args=None) -> None:
    print("Starting GovWifi Metrics Data Recovery...")

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

    # Step 3: Determine output path
    # If the user explicitly customized the year or month on the command line,
    # we prioritize the dynamic paths derived from their selection.
    is_cli_override = (parsed_args.year is not None) or (parsed_args.month is not None)

    output_path = None
    if is_cli_override:
        if month is not None:
            output_path = f"{year}_{month:02d}_govwifi_data.json"
        else:
            output_path = f"{year}_govwifi_data.json"

    try:
        recover_metrics(year=year, month=month, output_path=output_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
