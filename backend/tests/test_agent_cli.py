from typer.testing import CliRunner

from ped_agent_server.cli import app


def test_agent_cli_lists_doctor_and_vector_rebuild_commands() -> None:
    result = CliRunner().invoke(app, ["agent", "--help"])

    assert result.exit_code == 0
    assert "doctor" in result.stdout
    assert "rebuild-vector-index" in result.stdout


def test_agent_doctor_masks_environment_secrets() -> None:
    result = CliRunner().invoke(
        app,
        ["agent", "doctor"],
        env={
            "PED_AGENT_ANSWER__MODEL": "gpt-test",
            "PED_AGENT_ANSWER__API_KEY": "answer-secret",
            "PED_AGENT_VERIFY__ENABLED": "false",
            "PED_AGENT_EMBEDDING__MODEL": "embed-test",
            "PED_AGENT_EMBEDDING__API_KEY": "embedding-secret",
        },
    )

    assert result.exit_code == 0
    assert '"configuration": "ok"' in result.stdout
    assert "answer-secret" not in result.stdout
    assert "embedding-secret" not in result.stdout
