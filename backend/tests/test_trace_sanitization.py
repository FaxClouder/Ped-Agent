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
