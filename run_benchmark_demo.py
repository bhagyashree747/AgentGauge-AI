import json
from datetime import datetime
from pathlib import Path

from benchmark.controller import run_benchmark


task = """
Write a Python function called is_palindrome(text).

Requirements:
- Ignore spaces and capitalization.
- Return True if the text is a palindrome.
- Return False otherwise.
- Handle empty strings and single-character strings.
"""

test_code = """
assert is_palindrome("Race car") is True
assert is_palindrome("hello") is False
assert is_palindrome("Madam") is True
assert is_palindrome("A man a plan a canal Panama") is True
assert is_palindrome("") is True
assert is_palindrome("a") is True
assert is_palindrome("Python") is False

print("ALL TESTS PASSED")
"""

print("=" * 55)
print("          AGENTGAUGE AI - FIRST BENCHMARK")
print("=" * 55)
print("\\nRunning DirectCoder and VerifyCoder.")
print("Gemini API calls may take several minutes.\\n")

results = run_benchmark(
    task=task,
    test_code=test_code,
    max_attempts=3,
    timeout=5,
)

output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

results["benchmark_id"] = "benchmark_001"
results["timestamp"] = datetime.now().astimezone().isoformat()

output_file = output_dir / "benchmark_001.json"

output_file.write_text(
    json.dumps(results, indent=4),
    encoding="utf-8",
)

print("\\n" + "=" * 55)
print("              BENCHMARK RESULTS")
print("=" * 55)

for agent_name in ("direct_coder", "verify_coder"):
    agent = results[agent_name]

    print(f"\\n{agent['agent']}")
    print("Success:", agent["success"])
    print("Attempts:", agent["attempts"])
    print("Latency:", agent["latency_seconds"], "seconds")
    print("Total tokens:", agent["total_tokens"])
    print("Tests passed:", agent["test_result"]["passed"])

print("\\nSaved results to:", output_file)
print("\\nBENCHMARK COMPLETED")
