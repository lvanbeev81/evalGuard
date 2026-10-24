"""Unit tests for EvalGuard deterministic assertions."""

import pytest
from evalguard.assertions.deterministic import (
    check_cost_budget,
    check_forbidden_patterns,
    check_json_schema,
    check_latency_budget,
    check_required_keywords,
)


def test_json_schema_valid():
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "confidence": {"type": "number"},
        },
        "required": ["summary", "confidence"],
    }
    output = '```json\n{"summary": "Test passed", "confidence": 0.98}\n```'
    result = check_json_schema(output, schema)
    assert result.passed is True
    assert result.score == 1.0


def test_json_schema_malformed_json():
    schema = {"type": "object"}
    output = "This is not JSON at all."
    result = check_json_schema(output, schema)
    assert result.passed is False
    assert "not valid JSON" in result.reason


def test_json_schema_missing_required_key():
    schema = {
        "type": "object",
        "properties": {"action": {"type": "string"}},
        "required": ["action"],
    }
    output = '{"other_key": 123}'
    result = check_json_schema(output, schema)
    assert result.passed is False
    assert "Schema validation failure" in result.reason


def test_forbidden_patterns_detected():
    patterns = [r"\bpassword\b", r"\bapi_key\b"]
    output = "Here is the result: your API_KEY is sk-12345"
    result = check_forbidden_patterns(output, patterns)
    assert result.passed is False
    assert result.score == 0.0
    assert r"\bapi_key\b" in result.metadata["matched_patterns"]


def test_forbidden_patterns_clean():
    patterns = [r"\bsecret\b"]
    output = "Operation completed with normal system logs."
    result = check_forbidden_patterns(output, patterns)
    assert result.passed is True
    assert result.score == 1.0


def test_required_keywords_coverage():
    keywords = ["refund", "processed", "confirmation_code"]
    output = "Your refund has been processed successfully."
    result = check_required_keywords(output, keywords)
    assert result.passed is False
    assert result.score == pytest.approx(2 / 3, 0.01)
    assert "confirmation_code" in result.metadata["missing_keywords"]


def test_latency_budget():
    pass_res = check_latency_budget(latency_ms=450.0, max_latency_ms=500.0)
    assert pass_res.passed is True

    fail_res = check_latency_budget(latency_ms=750.0, max_latency_ms=500.0)
    assert fail_res.passed is False


def test_cost_budget():
    pass_res = check_cost_budget(estimated_cost_usd=0.002, max_cost_usd=0.01)
    assert pass_res.passed is True

    fail_res = check_cost_budget(estimated_cost_usd=0.015, max_cost_usd=0.01)
    assert fail_res.passed is False
