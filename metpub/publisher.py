import tableauserverclient as TSC


def publish_hyper_extract(
    hyper_path: str,
    token_name: str,
    token_value: str,
    site_id: str,
    server_url: str,
    project_name: str,
    year: int,
    month: int | None = None,
) -> None:
    """Authenticates to Tableau Cloud and publishes a Hyper extract."""
    if month is not None:
        datasource_name = f"{year}-{month:02d} GovWifi Data"
    else:
        datasource_name = f"{year} GovWifi Data"

    print(f"Connecting to Tableau Cloud at {server_url}...")
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id)
    server = TSC.Server(server_url, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        print("Successfully authenticated!")

        # Find the target project ID
        req_option = TSC.RequestOptions()
        req_option.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.Equals,
                project_name,
            )
        )
        all_projects, _ = server.projects.get(req_option)

        if not all_projects:
            raise ValueError(f"Project '{project_name}' not found.")

        target_project_id = all_projects[0].id

        # Define the Datasource Item
        new_datasource = TSC.DatasourceItem(target_project_id, name=datasource_name)

        # Set the publish mode (Overwrite, CreateNew, or Append)
        publish_mode = TSC.Server.PublishMode.Overwrite

        print(f"Publishing {hyper_path} as '{datasource_name}'...")
        published_datasource = server.datasources.publish(
            new_datasource, hyper_path, publish_mode
        )

        print(f"Success! Datasource published with ID: " f"{published_datasource.id}")
