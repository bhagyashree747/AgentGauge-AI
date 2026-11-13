import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import benchmark.controller as controller


task = """
Write a Python function called is_palindrome(text).
Ignore spaces and capitalization.
Return True for palindromes and False otherwise.
"""

test_code = """
assert is_palindrome("Race car") is True
assert is_palindrome("hello") is False
assert is_palindrome("Madam") is True
assert is_palindrome("A man a plan a canal Panama") is True
assert is_palindrome("") is True
assert is_palindrome("a") is True

print("ALL TESTS PASSED")
"""

incorrect_response = {
    "text": """
def is_palindrome(text):
    return text == text[::-1]
""",
    "model": "mock-demo",
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
    "thought_tokens": None,
}

correct_response = {
    "text": """
def is_palindrome(text):
    cleaned = "".join(
        character.lower()
        for character in str(text)
        if not character.isspace()
    )
    return cleaned == cleaned[::-1]
""",
    "model": "mock-demo",
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
    "thought_tokens": None,
}

print("=" * 55)
print("       AGENTGAUGE AI - OFFLINE DEMONSTRATION")
print("=" * 55)

with (
    patch(
        "agents.direct_coder.generate_text",
        return_value=incorrect_response,
    ),
    patch(
        "agents.verify_coder.generate_text",
        side_effect=[incorrect_response, correct_response],
    ),
):
    results = controller.run_benchmark(
        task=task,
        test_code=test_code,
        max_attempts=3,
        timeout=5,
    )

results["execution_mode"] = "MOCK DEMONSTRATION - NOT LIVE GEMINI"
results["timestamp"] = datetime.now().astimezone().isoformat()
results["notes"] = (
    "Controlled mock responses used to demonstrate the benchmark "
    "workflow. These are not real Gemini performance measurements."
)

for agent_name in ("direct_coder", "verify_coder"):
    agent = results[agent_name]
    agent["model"] = "mock-demo"
    agent["prompt_tokens"] = None
    agent["completion_tokens"] = None
    agent["total_tokens"] = None
    agent["thought_tokens"] = None

for metric in results["comparison"]["metrics"]:
    if metric["metric"] == "Total tokens":
        metric["direct_coder"] = None
        metric["verify_coder"] = None

output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "benchmark_mock_demo.json"

output_file.write_text(
    json.dumps(results, indent=4),
    encoding="utf-8",
)

print("\\n===== COMPARISON RESULTS =====")

for name in ("direct_coder", "verify_coder"):
    agent = results[name]

    print("\\n" + agent["agent"])
    print("Success:", agent["success"])
    print("Attempts:", agent["attempts"])
    print("Tests passed:", agent["test_result"]["passed"])
    print("Latency:", agent["latency_seconds"], "seconds")

print("\\n===== DEMONSTRATION STATUS =====")
print("DirectCoder:", results["direct_coder"]["success"])
print("VerifyCoder:", results["verify_coder"]["success"])
print("Saved:", output_file)
print("Mode:", results["execution_mode"])
