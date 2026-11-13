import time

from agents.direct_coder import run_direct_coder
from agents.verify_coder import run_verify_coder
from benchmark.metrics import build_comparison
from benchmark.test_runner import run_tests


def run_benchmark(
    task: str,
    test_code: str,
    max_attempts: int = 3,
    timeout: int = 5,
) -> dict:
    """
    Run DirectCoder and VerifyCoder on the same task and test suite.
    Return their results and a side-by-side comparison.
    """

    if not task or not task.strip():
        raise ValueError("Benchmark task cannot be empty.")

    if not test_code or not test_code.strip():
        raise ValueError("Benchmark test code cannot be empty.")

    # --------------------------------------------------
    # 1. Run DirectCoder
    # --------------------------------------------------
    direct_start = time.perf_counter()

    direct_generation = run_direct_coder(task)

    direct_test_result = run_tests(
        code=direct_generation["code"],
        test_code=test_code,
        timeout=timeout,
    )

    direct_latency = round(time.perf_counter() - direct_start, 3)

    direct_result = {
        "agent": "DirectCoder",
        "code": direct_generation["code"],
        "model": direct_generation.get("model"),
        "success": direct_test_result["passed"],
        "attempts": 1,
        "latency_seconds": direct_latency,
        "test_latency_seconds": direct_test_result["latency_seconds"],
        "test_result": direct_test_result,
        "prompt_tokens": direct_generation.get("prompt_tokens") or 0,
        "completion_tokens": direct_generation.get("completion_tokens") or 0,
        "total_tokens": direct_generation.get("total_tokens") or 0,
        "thought_tokens": direct_generation.get("thought_tokens") or 0,
    }

    # --------------------------------------------------
    # 2. Run VerifyCoder with the same task and tests
    # --------------------------------------------------
    verify_generation = run_verify_coder(
        task=task,
        test_code=test_code,
        max_attempts=max_attempts,
        timeout=timeout,
    )

    verify_result = {
        "agent": "VerifyCoder",
        "code": verify_generation["code"],
        "model": verify_generation.get("model"),
        "success": verify_generation["success"],
        "attempts": verify_generation["attempts"],
        "latency_seconds": verify_generation["latency_seconds"],
        "test_latency_seconds": verify_generation["test_latency_seconds"],
        "test_result": verify_generation["test_result"],
        "prompt_tokens": verify_generation["prompt_tokens"],
        "completion_tokens": verify_generation["completion_tokens"],
        "total_tokens": verify_generation["total_tokens"],
        "thought_tokens": verify_generation["thought_tokens"],
    }

    # --------------------------------------------------
    # 3. Build comparison
    # --------------------------------------------------
    comparison = build_comparison(direct_result, verify_result)

    return {
        "task": task,
        "model": direct_result["model"],
        "direct_coder": direct_result,
        "verify_coder": verify_result,
        "comparison": comparison,
    }
