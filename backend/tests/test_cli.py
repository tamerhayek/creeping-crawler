from click.testing import CliRunner

import main


def test_list_urls_command_prints_all_available_urls() -> None:
    runner = CliRunner()

    result = runner.invoke(main.cli, ["list-urls"])

    assert result.exit_code == 0
    assert result.output.strip().splitlines() == main.AVAILABLE_URLS


def test_run_command_rejects_unknown_url() -> None:
    runner = CliRunner()

    result = runner.invoke(main.cli, ["run", "--url", "https://example.com"])

    assert result.exit_code != 0
    assert "Invalid value for '--url'" in result.output


def test_run_command_requires_url() -> None:
    runner = CliRunner()

    result = runner.invoke(main.cli, ["run"])

    assert result.exit_code != 0
    assert "Missing option '--url'" in result.output
