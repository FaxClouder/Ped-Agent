import pytest

from ped_agent_server.settings import load_settings


def clear_agent_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PED_AGENT_ANSWER__PROTOCOL",
        "PED_AGENT_ANSWER__MODEL",
        "PED_AGENT_ANSWER__API_KEY",
        "PED_AGENT_VERIFY__ENABLED",
        "PED_AGENT_VERIFY__PROTOCOL",
        "PED_AGENT_EMBEDDING__MODEL",
        "PED_AGENT_EMBEDDING__API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_settings_load_nested_roles_and_mask_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__PROTOCOL", "openai_compatible")
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "deepseek-chat")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "answer-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "true")
    monkeypatch.setenv("PED_AGENT_VERIFY__PROTOCOL", "inherit")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "text-embedding-3-small")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")

    settings = load_settings(env_file=None)

    assert settings.answer.model == "deepseek-chat"
    assert settings.verify.protocol == "inherit"
    assert settings.embedding.model == "text-embedding-3-small"
    assert settings.resolved_verify.model == settings.answer.model
    rendered = repr(settings) + str(settings.model_dump())
    assert "answer-secret" not in rendered
    assert "embedding-secret" not in rendered


def test_settings_accept_legacy_provider_key(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__PROTOCOL", "anthropic")
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "claude-sonnet-4-20250514")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "legacy-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "false")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "text-embedding-3-small")
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-embedding-secret")

    settings = load_settings(env_file=None)

    assert settings.answer.api_key is not None
    assert settings.answer.api_key.get_secret_value() == "legacy-secret"
    assert settings.embedding.api_key is not None
    assert settings.embedding.api_key.get_secret_value() == "legacy-embedding-secret"


def test_settings_reject_missing_required_agent_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "gpt-test")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "false")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")

    with pytest.raises(ValueError, match="answer API key"):
        load_settings(env_file=None)

