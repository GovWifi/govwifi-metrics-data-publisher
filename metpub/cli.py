import sys

from metpub.config import config
from metpub.converter import convert_json_to_hyper
from metpub.publisher import publish_hyper_extract


def main() -> None:
    print("Starting GovWifi Metrics Data Publisher...")

    try:
        # Step 1: Convert JSON to Hyper
        convert_json_to_hyper(
            json_path=config.JSON_FILE_PATH,
            hyper_path=config.HYPER_FILE_PATH,
            table_name=config.TABLE_NAME,
        )

        # Step 2: Publish to Tableau
        publish_hyper_extract(
            hyper_path=config.HYPER_FILE_PATH,
            token_name=config.TOKEN_NAME,
            token_value=config.TOKEN_VALUE,
            site_id=config.SITE_ID,
            server_url=config.SERVER_URL,
            project_name=config.PROJECT_NAME,
            datasource_name=config.DATASOURCE_NAME,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
