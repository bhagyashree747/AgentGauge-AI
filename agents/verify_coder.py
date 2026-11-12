import time

from agents.direct_coder import clean_code
from benchmark.test_runner import run_tests
from services.gemini_client import generate_text


def _add_usage(totals: dict, result: dict) -> None:
    """Add token usage from one Gemini request."""
    for key in (
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "thought_tokens",
    ):
        value = result.get(key)
        if isinstance(value, (int, float)):
            totals[key] += value


def run_verify_coder(
    task: str,
    test_code: str,
    max_attempts: int = 3,
    timeout: int = 5,
) -> dict:
    """
    Generate code, execute benchmark tests, and request corrections
    when tests fail. This runner is intended for trusted benchmark tasks.
    """

    if not task or not task.strip():
        raise ValueError("Task cannot be empty.")

    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    if not isinstance(max_attempts, int) or not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3.")

    if not isinstance(timeout, int) or timeout < 1:
        raise ValueError("timeout must be a positive integer.")

    start_time = time.perf_counter()
    totals = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "thought_tokens": 0,
    }

    test_latency = 0.0
    code = ""
    test_result = None

    system_instruction = (
        "You are VerifyCoder, a careful Python coding agent. "
        "Solve the user's programming task and return only the complete "
        "Python source code. Do not include Markdown fences or explanations. "
        "Consider edge cases and make sure the solution matches the task."
    )

    prompt = (
        f"PROGRAMMING TASK:\n{task.strip()}\n\n"
        "Write a complete Python solution that satisfies this task."
    )

    for attempt in range(1, max_attempts + 1):
        response = generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
        )
        _add_usage(totals, response)

        code = clean_code(response["text"])

        test_result = run_tests(
            code=code,
            test_code=test_code,
            timeout=timeout,
        )
        test_latency += test_result["latency_seconds"]

        if test_result["passed"]:
            break

        if attempt < max_attempts:
            prompt = (
                f"ORIGINAL PROGRAMMING TASK:\n{task.strip()}\n\n"
                f"YOUR PREVIOUS CODE:\n{code}\n\n"
                f"TEST OUTPUT:\n{test_result['stdout']}\n\n"
                f"TEST ERROR:\n{test_result['stderr']}\n\n"
                f"FAILURE TYPE:\n{test_result['error']}\n\n"
                "The previous solution did not pass the tests. "
                "Find and fix the problem. Return the complete corrected "
                "Python source code only. Do not use Markdown fences."
            )

    return {
        "agent": "VerifyCoder",
        "code": code,
        "model": response.get("model"),
        "success": test_result["passed"],
        "attempts": attempt,
        "max_attempts": max_attempts,
        "test_result": test_result,
        "latency_seconds": round(time.perf_counter() - start_time, 3),
        "test_latency_seconds": round(test_latency, 3),
        **totals,
    }
