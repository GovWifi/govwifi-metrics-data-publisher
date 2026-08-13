from datetime import date

from metpub.token_health import check_token_expiry


def test_skips_when_not_configured(capsys):
    check_token_expiry("")

    out = capsys.readouterr().out
    assert "skipped" in out
    assert "WARNING" not in out


def test_warns_on_unparseable_date(capsys):
    check_token_expiry("not-a-date")

    out = capsys.readouterr().out
    assert "WARNING" in out
    assert "could not parse" in out


def test_ok_when_far_from_expiry(capsys):
    check_token_expiry("2027-02-01", today=date(2027, 1, 1))

    out = capsys.readouterr().out
    assert "OK" in out
    assert "WARNING" not in out


def test_warns_within_warning_window(capsys):
    check_token_expiry("2027-01-15", warning_days=30, today=date(2027, 1, 1))

    out = capsys.readouterr().out
    assert "WARNING: Tableau PAT expiry is in 14 day(s)" in out


def test_warns_when_already_expired(capsys):
    check_token_expiry("2026-12-25", today=date(2027, 1, 1))

    out = capsys.readouterr().out
    assert "WARNING: Tableau PAT expiry passed 7 day(s) ago" in out


def test_respects_custom_warning_days(capsys):
    check_token_expiry("2027-02-01", warning_days=60, today=date(2027, 1, 1))

    out = capsys.readouterr().out
    assert "WARNING: Tableau PAT expiry is in 31 day(s)" in out


def test_all_warning_branches_share_matchable_phrase(capsys):
    """CloudWatch matches the exact phrase 'WARNING: Tableau PAT expiry' as
    a plain-text log filter pattern (see govwifi-terraform govwifi-metrics/
    alarms.tf tableau_pat_expiry_warning) -- every branch that should alert
    must contain it verbatim.
    """
    check_token_expiry("2026-12-25", today=date(2027, 1, 1))
    check_token_expiry("2027-01-15", warning_days=30, today=date(2027, 1, 1))
    check_token_expiry("not-a-date")

    out = capsys.readouterr().out
    for line in out.splitlines():
        if "WARNING" in line:
            assert "WARNING: Tableau PAT expiry" in line
