import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run_tests(
    code: str,
    test_code: str,
    timeout: int = 5,
) -> dict:
    """
    Execute generated Python code with a predefined test suite.

    This is a timeout-controlled local runner, NOT a hardened sandbox.
    Use only trusted benchmark tasks and generated solutions.
    """

    if not code or not code.strip():
        raise ValueError("Generated code cannot be empty.")

    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    if len(code) > 20000:
        raise ValueError("Generated code exceeds the 20 KB limit.")

    if len(test_code) > 10000:
        raise ValueError("Test code exceeds the 10 KB limit.")

    try:
        compile(code, "<generated_solution>", "exec")
    except SyntaxError as error:
        return {
            "passed": False,
            "return_code": 1,
            "stdout": "",
            "stderr": f"SyntaxError: {error}",
            "latency_seconds": 0,
            "error": "syntax_error",
        }

    combined_code = (
        code.rstrip()
        + "\n\n# ===== BENCHMARK TESTS =====\n\n"
        + test_code.strip()
        + "\n"
    )

    start_time = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="agentgauge_") as temp_dir:
            script_path = Path(temp_dir) / "benchmark_solution.py"
            script_path.write_text(combined_code, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )

        latency = time.perf_counter() - start_time

        return {
            "passed": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-5000:],
            "latency_seconds": round(latency, 3),
            "error": None if result.returncode == 0 else "test_failure",
        }

    except subprocess.TimeoutExpired as error:
        latency = time.perf_counter() - start_time

        return {
            "passed": False,
            "return_code": -1,
            "stdout": str(error.stdout or "")[-5000:],
            "stderr": f"Execution exceeded the {timeout}-second timeout.",
            "latency_seconds": round(latency, 3),
            "error": "timeout",
        }
