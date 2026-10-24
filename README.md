# EvalGuard: Deterministic Evaluation & Guardrail Harness for AI Agents

[![CI](https://github.com/your-username/evalguard/actions/workflows/eval_ci.yml/badge.svg)](https://github.com/your-username/evalguard/actions)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**EvalGuard** is a lightweight, high-performance evaluation harness and CI/CD quality gate for AI agents and LLM applications. It provides automated benchmarking across schema compliance, forbidden pattern detection, latency SLAs, token budgets, and semantic accuracy.

---

## The Problem: Silent Failure in Production AI

Most production LLM failures do not raise fatal Python exceptions. Instead, they fail **silently and nondeterministically**:
* **Schema Drift:** Generating markdown or malformed JSON that breaks downstream parser pipelines.
* **Cost & Latency Spikes:** Unbounded reasoning loops consuming excessive tokens or violating user SLAs.
* **Safety & Data Leakage:** Outputting forbidden tokens, internal instructions, or simulated credentials.
* **Flaky Evaluations:** Relying solely on expensive, non-deterministic "LLM-as-a-judge" grading instead of fast, deterministic assertions.

EvalGuard enforces a **two-tiered evaluation hierarchy**:
1. **L1 Deterministic Guardrails (Sub-millisecond, $0.00 Cost):** Hard-gated schema validation, regex scanning, keyword presence, and latency/cost budget enforcement.
2. **L2 Semantic & Model-Based Checks:** Jaccard token overlap and structured rubric grading with explicit reasoning traces.

---

## Architecture Overview

```
                      ┌─────────────────────────────────┐
                      │    Input Prompt & Context       │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │    Target AI Agent / Pipeline   │
                      └────────────────┬────────────────┘
                                       │
                         [Actual Output + Latency]
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
      [ Tier 1: L1 Deterministic ]              [ Tier 2: L2 Semantic ]
    ├─ JSON Schema Validation (Pydantic)      ├─ Token Similarity Overlap
    ├─ Forbidden Pattern Scanner (Regex)      └─ LLM-as-a-Judge Rubric
    ├─ Required Keyword Adherence
    └─ Latency & Cost Budget Caps
                 │                                           │
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │    Rich Terminal Dashboard      │
                      │    & Exit-Code CI/CD Gate       │
                      │ (Exit 0 = Pass, Exit 1 = Fail)  │
                      └─────────────────────────────────┘
```

---

## Quickstart

### 1. Installation

Clone and install in editable mode:
```bash
git clone https://github.com/your-username/evalguard.git
cd evalguard
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Validate a Test Suite File
Verify JSON/JSONL syntax before running evaluations:
```bash
evalguard validate examples/customer_support_suite.jsonl
```

### 3. Run Benchmark Suite & CI Quality Gate
Execute the evaluation suite with a minimum 80% pass threshold:
```bash
evalguard run examples/customer_support_suite.jsonl --threshold 0.80 --concurrency 4 -o reports/report.json
```

---

## Test Suite Schema Example (`.jsonl`)

Each line in a test suite file represents an individual benchmark case:

```json
{
  "id": "tc_sql_agent_001",
  "input_prompt": "Retrieve all active customer accounts created after 2024-01-01.",
  "expected_schema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "is_read_only": { "type": "boolean" }
    },
    "required": ["query", "is_read_only"]
  },
  "forbidden_patterns": ["DROP TABLE", "DELETE FROM", "UPDATE ", "ALTER "],
  "required_keywords": ["SELECT", "FROM", "WHERE"],
  "max_latency_ms": 750.0,
  "max_cost_usd": 0.02
}
```

---

## Terminal Dashboard Output

```
EvalGuard Benchmark Suite: customer_support_suite
Deterministic Verification & Guardrail Audit

Test Case Assertion Receipts:
+----------------+---------+--------------------+--------+---------------------------------------+
| Case ID        | Latency | Assertion          | Status | Details                               |
+----------------+---------+--------------------+--------+---------------------------------------+
| tc_refund_001  |  50.5ms | json_schema        |  PASS  | JSON schema validation passed.        |
|                |         | forbidden_patterns |  PASS  | No forbidden patterns detected.       |
|                |         | required_keywords  |  PASS  | All 2 required keywords present.      |
|                |         | latency_budget     |  PASS  | Latency 50.5ms within SLA (1000.0ms). |
|                |         | cost_budget        |  PASS  | Cost $0.00034 within budget ($0.05).  |
| tc_sql_002     |  52.0ms | json_schema        |  PASS  | JSON schema validation passed.        |
|                |         | forbidden_patterns |  PASS  | No forbidden patterns detected.       |
+----------------+---------+--------------------+--------+---------------------------------------+

Suite Execution Summary:
  Total Test Cases: 3
  Passed Cases:     3
  Failed Cases:     0
  Pass Rate:        100.0% (PASSED >= 80%)
  Mean Latency:     51.7 ms
  Estimated Cost:   $0.00072 USD

All quality gates satisfied.
```

---

## CI/CD Automation (GitHub Actions)

EvalGuard integrates directly with GitHub Actions (`.github/workflows/eval_ci.yml`). Any pull request that causes schema regressions, SLA violations, or unapproved prompt leakage will return exit code `1`, blocking merges before reaching production.

---

## Testing

Run unit tests across all assertion engines:
```bash
pytest tests/ -v
```

---

## License

MIT License. Free for personal and commercial portfolio use.
