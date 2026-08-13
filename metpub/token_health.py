from datetime import date, datetime

DEFAULT_WARNING_DAYS = 30


def check_token_expiry(
    expires_at: str, warning_days: int = DEFAULT_WARNING_DAYS, today: date | None = None
) -> None:
    """Logs the Tableau PAT's remaining lifetime to stdout.

    This never raises: a PAT nearing expiry should not block today's
    publication, which still works. A CloudWatch alarm watches the CodeBuild
    log group for the "WARNING: Tableau PAT expiry" phrase used by every
    warning branch below (matched as an exact phrase, so keep it verbatim
    if you touch this), giving ops an early nudge to rotate the token in
    Secrets Manager before it actually expires and publication starts
    failing outright.
    """
    if not expires_at:
        print(
            "Tableau PAT expiry check skipped: TOKEN_EXPIRES_AT is not set "
            "in the govwifi/metrics-data-publisher/tableau secret."
        )
        return

    try:
        expiry_date = datetime.fromisoformat(expires_at).date()
    except ValueError:
        print(
            f"WARNING: Tableau PAT expiry check failed: could not parse "
            f"TOKEN_EXPIRES_AT value '{expires_at}' as an ISO date "
            f"(expected YYYY-MM-DD)."
        )
        return

    today = today or date.today()
    days_remaining = (expiry_date - today).days

    if days_remaining < 0:
        print(
            f"WARNING: Tableau PAT expiry passed {abs(days_remaining)} "
            f"day(s) ago (on {expiry_date}). Rotate it immediately: see "
            f"runbook https://docs.wifi.service.gov.uk/infrastructure/"
            f"monitoring#rotating-the-tableau-personal-access-token"
        )
    elif days_remaining <= warning_days:
        print(
            f"WARNING: Tableau PAT expiry is in {days_remaining} day(s) "
            f"(on {expiry_date}). Rotate it before it expires: see runbook "
            f"https://docs.wifi.service.gov.uk/infrastructure/monitoring"
            f"#rotating-the-tableau-personal-access-token"
        )
    else:
        print(
            f"Tableau PAT expiry check OK: {days_remaining} day(s) "
            f"remaining (expires {expiry_date})."
        )
