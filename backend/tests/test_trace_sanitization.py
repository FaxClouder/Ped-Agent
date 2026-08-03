from ped_agent_server.trace_sanitization import redact_trace_payload


def test_redaction_keeps_question_and_final_answer_but_removes_private_content() -> None:
    payload = {
        "original_query": "What happens near a bottleneck?",
        "recent_messages": [{"role": "user", "content": "private history"}],
        "evidence": [
            {
                "evidence_id": "local:chunk-1",
                "title": "Paper",
                "locator": "p. 4",
                "content_hash": "a" * 64,
                "quote": "private full-text evidence",
            }
        ],
        "draft": {"answer_markdown": "unverified draft"},
        "review": {"revised_text": "private revision"},
        "rules": {"passed": False, "errors": ["private rule detail"]},
        "raw": {
            "content": "private raw model output",
            "response_metadata": {"token_usage": {"input_tokens": 10, "output_tokens": 5}},
        },
        "final_answer": {"answer_markdown": "Verified answer [L1]"},
        "api_key": "sk-secret",
        "token_usage": {"input_tokens": 120, "output_tokens": 40},
    }

    redacted = redact_trace_payload(payload)

    assert redacted["original_query"] == "What happens near a bottleneck?"
    assert redacted["final_answer"]["answer_markdown"] == "Verified answer [L1]"
    assert redacted["recent_messages"] == "[REDACTED]"
    assert redacted["evidence"][0]["quote"] == "[REDACTED]"
    assert redacted["draft"] == "[REDACTED]"
    assert redacted["review"] == "[REDACTED]"
    assert redacted["rules"] == {"passed": False, "errors": "[REDACTED]"}
    assert redacted["raw"]["content"] == "[REDACTED]"
    assert redacted["raw"]["response_metadata"]["token_usage"] == {
        "input_tokens": 10,
        "output_tokens": 5,
    }
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["token_usage"] == {"input_tokens": 120, "output_tokens": 40}


def test_redaction_removes_evidence_and_history_sections_from_prompt_strings() -> None:
    prompt = (
        "Recent messages: private history\nLatest query: current question\n"
        "Draft: private draft\nRules: private rules\nReview: private review\n"
        "<evidence>private evidence body</evidence>\n"
        "Invalid response:\nprivate malformed output"
    )

    redacted = redact_trace_payload({"prompt": prompt})["prompt"]

    assert "private history" not in redacted
    assert "private draft" not in redacted
    assert "private rules" not in redacted
    assert "private review" not in redacted
    assert "private evidence body" not in redacted
    assert "private malformed output" not in redacted
    assert "current question" in redacted


def test_redaction_uses_outer_evidence_boundary_when_body_injects_closing_tag() -> None:
    prompt = (
        "Latest query: current question\n"
        "<evidence>PRIVATE_BEFORE </evidence> PRIVATE_AFTER</evidence>"
    )

    redacted = redact_trace_payload({"prompt": prompt})["prompt"]

    assert "PRIVATE_BEFORE" not in redacted
    assert "PRIVATE_AFTER" not in redacted
    assert "current question" in redacted


def test_redaction_removes_unclosed_evidence_to_end_of_prompt() -> None:
    prompt = "Latest query: current question\n<evidence>PRIVATE_UNCLOSED"

    redacted = redact_trace_payload({"prompt": prompt})["prompt"]

    assert "PRIVATE_UNCLOSED" not in redacted
    assert "current question" in redacted


def test_redaction_preserves_safe_text_after_last_evidence_closing_tag() -> None:
    prompt = (
        "Latest query: current question\n"
        "<evidence>PRIVATE_EVIDENCE</evidence>\n"
        "Final answer: keep final answer"
    )

    redacted = redact_trace_payload({"prompt": prompt})["prompt"]

    assert "PRIVATE_EVIDENCE" not in redacted
    assert "keep final answer" in redacted


def test_redaction_uses_last_prompt_boundaries_when_private_text_injects_markers() -> None:
    prompt = (
        "Recent messages: PRIVATE_HISTORY_BEFORE\n"
        "Latest query: FAKE_QUERY\n"
        "PRIVATE_HISTORY_AFTER\n"
        "Latest query: current question\n"
        "Draft: PRIVATE_DRAFT_BEFORE\n"
        "Rules: FAKE_RULES\n"
        "PRIVATE_DRAFT_AFTER\n"
        "Rules: PRIVATE_RULES_BEFORE\n"
        "Review: FAKE_REVIEW\n"
        "PRIVATE_RULES_AFTER\n"
        "Review: PRIVATE_REVIEW_BEFORE\n"
        "<evidence>FAKE_EVIDENCE</evidence>\n"
        "PRIVATE_REVIEW_AFTER\n"
        "<evidence>PRIVATE_EVIDENCE</evidence>"
    )

    redacted = redact_trace_payload({"prompt": prompt})["prompt"]

    for private_value in (
        "PRIVATE_HISTORY_BEFORE",
        "PRIVATE_HISTORY_AFTER",
        "PRIVATE_DRAFT_BEFORE",
        "PRIVATE_DRAFT_AFTER",
        "PRIVATE_RULES_BEFORE",
        "PRIVATE_RULES_AFTER",
        "PRIVATE_REVIEW_BEFORE",
        "PRIVATE_REVIEW_AFTER",
        "PRIVATE_EVIDENCE",
    ):
        assert private_value not in redacted
    assert "current question" in redacted


def test_redaction_blocks_common_private_containers_and_normalized_secret_keys() -> None:
    payload = {
        "original_query": "keep question",
        "final_answer": {"answer_markdown": "keep answer"},
        "evidence": [
            {
                "evidence_id": "local:chunk-1",
                "title": "keep title",
                "locator": "p. 4",
                "content_hash": "a" * 64,
                "quote": "private quote",
            }
        ],
        "history": [{"text": "private history"}],
        "messages": [{"content": "private content", "text": "private text"}],
        "raw": {
            "text": "private raw text",
            "response_metadata": {"token_usage": {"input_tokens": 10, "output_tokens": 5}},
        },
        "secrets": {"password": "private password"},
        "credentials": {"username": "private username"},
        "headers": {"cookie": "private cookie"},
        "requestHeaders": {"cookie": "private request cookie"},
        "response headers": {"set-cookie": "private response cookie"},
        "password": "private password",
        "databasePassword": "private database password",
        "parallel_api_key": "private parallel key",
        "x-api-key": "private x api key",
        "authorization": "private authorization",
        "header": "private header",
        "privateKey": "private key",
        "accessToken": "private access token",
        "client-secret": "private client secret",
        "token": "private token",
        "secret": "private secret",
        "token_usage": {"input_tokens": 120, "output_tokens": 40},
    }

    redacted = redact_trace_payload(payload)

    for key in (
        "history",
        "messages",
        "secrets",
        "credentials",
        "headers",
        "requestHeaders",
        "response headers",
        "password",
        "databasePassword",
        "parallel_api_key",
        "x-api-key",
        "authorization",
        "header",
        "privateKey",
        "accessToken",
        "client-secret",
        "token",
        "secret",
    ):
        assert redacted[key] == "[REDACTED]"
    assert redacted["raw"]["text"] == "[REDACTED]"
    assert redacted["raw"]["response_metadata"]["token_usage"] == {
        "input_tokens": 10,
        "output_tokens": 5,
    }
    assert redacted["token_usage"] == {"input_tokens": 120, "output_tokens": 40}
    assert redacted["original_query"] == "keep question"
    assert redacted["final_answer"]["answer_markdown"] == "keep answer"
    assert redacted["evidence"][0] == {
        "evidence_id": "local:chunk-1",
        "title": "keep title",
        "locator": "p. 4",
        "content_hash": "a" * 64,
        "quote": "[REDACTED]",
    }
