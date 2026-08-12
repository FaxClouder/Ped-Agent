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
            "PED_AGENT_ANSWER__PROTOCOL": "openai_compatible",
            "PED_AGENT_ANSWER__MODEL": "deepseek-v4-flash",
            "PED_AGENT_ANSWER__API_KEY": "answer-secret",
            "PED_AGENT_ANSWER__BASE_URL": "https://api.deepseek.com",
            "PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD": "json_mode",
            "PED_AGENT_VERIFY__ENABLED": "true",
            "PED_AGENT_VERIFY__PROTOCOL": "inherit",
            "PED_AGENT_VERIFY__MODEL": "deepseek-v4-pro",
            "PED_AGENT_EMBEDDING__PROTOCOL": "openai_compatible",
            "PED_AGENT_EMBEDDING__MODEL": "embed-test",
            "PED_AGENT_EMBEDDING__API_KEY": "embedding-secret",
            "PED_AGENT_LANGSMITH__ENABLED": "true",
            "PED_AGENT_LANGSMITH__API_KEY": "langsmith-secret",
            "PED_AGENT_LANGSMITH__PROJECT": "ped-agent-test",
            "PED_AGENT_LANGSMITH__SAMPLING_RATE": "1.0",
            "PED_AGENT_LANGSMITH__CONTENT_POLICY": "redacted",
            "PED_AGENT_LANGSMITH__ENDPOINT": (
                "https://trace.example.test/v1?token=endpoint-secret"
            ),
        },
    )

    assert result.exit_code == 0
    assert '"configuration": "ok"' in result.stdout
    assert '"model": "deepseek-v4-flash"' in result.stdout
    assert '"structured_output_method": "json_mode"' in result.stdout
    assert '"model": "deepseek-v4-pro"' in result.stdout
    assert '"content_policy": "redacted"' in result.stdout
    assert '"sampling_rate": 1.0' in result.stdout
    assert "answer-secret" not in result.stdout
    assert "embedding-secret" not in result.stdout
    assert "langsmith-secret" not in result.stdout
    assert "endpoint-secret" not in result.stdout


def test_agent_doctor_reports_disabled_verifier_without_secrets() -> None:
    result = CliRunner().invoke(
        app,
        ["agent", "doctor"],
        env={
            "PED_AGENT_ANSWER__MODEL": "deepseek-v4-flash",
            "PED_AGENT_ANSWER__API_KEY": "answer-secret",
            "PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD": "json_mode",
            "PED_AGENT_VERIFY__ENABLED": "false",
            "PED_AGENT_VERIFY__API_KEY": "verify-secret",
            "PED_AGENT_EMBEDDING__PROTOCOL": "openai_compatible",
            "PED_AGENT_EMBEDDING__MODEL": "embed-test",
            "PED_AGENT_EMBEDDING__API_KEY": "embedding-secret",
            "PED_AGENT_LANGSMITH__ENABLED": "false",
            "PED_AGENT_LANGSMITH__API_KEY": "langsmith-secret",
        },
    )

    assert result.exit_code == 0
    assert '"enabled": false' in result.stdout
    assert '"protocol": "disabled"' in result.stdout
    assert '"model": null' in result.stdout
    assert '"structured_output_method": null' in result.stdout
    for secret in (
        "answer-secret",
        "verify-secret",
        "embedding-secret",
        "langsmith-secret",
    ):
        assert secret not in result.stdout
