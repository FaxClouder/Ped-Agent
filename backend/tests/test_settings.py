import pytest

from ped_agent_server.settings import load_settings


def clear_agent_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PED_AGENT_ANSWER__PROTOCOL",
        "PED_AGENT_ANSWER__MODEL",
        "PED_AGENT_ANSWER__API_KEY",
        "PED_AGENT_ANSWER__BASE_URL",
        "PED_AGENT_ANSWER__TEMPERATURE",
        "PED_AGENT_ANSWER__MAX_TOKENS",
        "PED_AGENT_ANSWER__TIMEOUT_SECONDS",
        "PED_AGENT_ANSWER__MAX_RETRIES",
        "PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD",
        "PED_AGENT_VERIFY__ENABLED",
        "PED_AGENT_VERIFY__PROTOCOL",
        "PED_AGENT_VERIFY__MODEL",
        "PED_AGENT_VERIFY__API_KEY",
        "PED_AGENT_VERIFY__BASE_URL",
        "PED_AGENT_VERIFY__TEMPERATURE",
        "PED_AGENT_VERIFY__MAX_TOKENS",
        "PED_AGENT_VERIFY__TIMEOUT_SECONDS",
        "PED_AGENT_VERIFY__MAX_RETRIES",
        "PED_AGENT_VERIFY__STRUCTURED_OUTPUT_METHOD",
        "PED_AGENT_EMBEDDING__MODEL",
        "PED_AGENT_EMBEDDING__API_KEY",
        "PED_AGENT_LANGSMITH__ENABLED",
        "PED_AGENT_LANGSMITH__API_KEY",
        "PED_AGENT_LANGSMITH__PROJECT",
        "PED_AGENT_LANGSMITH__SAMPLING_RATE",
        "PED_AGENT_LANGSMITH__CONTENT_POLICY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "LANGSMITH_API_KEY",
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


def test_settings_resolve_deepseek_json_mode_and_redacted_langsmith(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "deepseek-v4-flash")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "deepseek-secret")
    monkeypatch.setenv("PED_AGENT_ANSWER__BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD", "json_mode")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "true")
    monkeypatch.setenv("PED_AGENT_VERIFY__PROTOCOL", "inherit")
    monkeypatch.setenv("PED_AGENT_VERIFY__MODEL", "deepseek-v4-pro")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__ENABLED", "true")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__API_KEY", "langsmith-secret")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__PROJECT", "ped-agent-local")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__SAMPLING_RATE", "1.0")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__CONTENT_POLICY", "redacted")

    settings = load_settings(env_file=None)

    assert settings.answer.structured_output_method == "json_mode"
    assert settings.resolved_verify.model == "deepseek-v4-pro"
    assert settings.resolved_verify.api_key.get_secret_value() == "deepseek-secret"
    assert settings.resolved_verify.structured_output_method == "json_mode"
    assert settings.langsmith.project == "ped-agent-local"
    assert settings.langsmith.sampling_rate == 1.0
    assert settings.langsmith.content_policy == "redacted"


def test_settings_reject_non_redacted_langsmith_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "deepseek-v4-flash")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "answer-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "false")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__CONTENT_POLICY", "full")

    with pytest.raises(ValueError, match="content_policy"):
        load_settings(env_file=None)


def test_settings_resolve_explicit_verify_zero_values_and_inherit_output_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_agent_env(monkeypatch)
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "deepseek-v4-flash")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "answer-secret")
    monkeypatch.setenv("PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD", "json_mode")
    monkeypatch.setenv("PED_AGENT_VERIFY__PROTOCOL", "anthropic")
    monkeypatch.setenv("PED_AGENT_VERIFY__MODEL", "verify-test")
    monkeypatch.setenv("PED_AGENT_VERIFY__API_KEY", "verify-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__TEMPERATURE", "0.0")
    monkeypatch.setenv("PED_AGENT_VERIFY__MAX_TOKENS", "0")
    monkeypatch.setenv("PED_AGENT_VERIFY__TIMEOUT_SECONDS", "0.0")
    monkeypatch.setenv("PED_AGENT_VERIFY__MAX_RETRIES", "0")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")

    resolved = load_settings(env_file=None).resolved_verify

    assert resolved.temperature == 0.0
    assert resolved.max_tokens == 0
    assert resolved.timeout_seconds == 0.0
    assert resolved.max_retries == 0
    assert resolved.structured_output_method == "json_mode"
