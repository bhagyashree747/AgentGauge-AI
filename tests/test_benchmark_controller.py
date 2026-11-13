from unittest.mock import patch

from benchmark.controller import run_benchmark


def test_benchmark_runs_both_agents_and_compares_results():
    task = "Write a Python function to add two numbers."
    test_code = 'assert add(2, 3) == 5'

    direct_response = {
        "code": "def add(a, b):\n    return a + b",
        "model": "gemini-3.8-flash",
        "latency_seconds": 10.0,
        "prompt_tokens": 100,
        "completion_tokens": 30,
        "total_tokens": 130,
        "thought_tokens": 0,
    }

    verify_response = {
        "code": "def add(a, b):\n    return a + b",
        "model": "gemini-3.8-flash",
        "success": True,
        "attempts": 1,
        "latency_seconds": 12.0,
        "test_latency_seconds": 0.1,
        "test_result": {
            "passed": True,
            "return_code": 0,
            "stdout": "ALL TESTS PASSED",
            "stderr": "",
            "latency_seconds": 0.1,
            "error": None,
        },
        "prompt_tokens": 120,
        "completion_tokens": 35,
        "total_tokens": 155,
        "thought_tokens": 0,
    }

    successful_test = {
        "passed": True,
        "return_code": 0,
        "stdout": "ALL TESTS PASSED",
        "stderr": "",
        "latency_seconds": 0.1,
        "error": None,
    }

    with (
        patch(
            "benchmark.controller.run_direct_coder",
            return_value=direct_response,
        ) as mock_direct,
        patch(
            "benchmark.controller.run_verify_coder",
            return_value=verify_response,
        ) as mock_verify,
        patch(
            "benchmark.controller.run_tests",
            return_value=successful_test,
        ) as mock_tests,
    ):
        result = run_benchmark(task, test_code)

    mock_direct.assert_called_once_with(task)
    mock_verify.assert_called_once_with(
        task=task,
        test_code=test_code,
        max_attempts=3,
        timeout=5,
    )

    assert mock_tests.call_count == 1

    assert result["direct_coder"]["success"] is True
    assert result["verify_coder"]["success"] is True

    assert result["comparison"]["direct_coder_success"] is True
    assert result["comparison"]["verify_coder_success"] is True

    assert len(result["comparison"]["metrics"]) == 5

    print("BENCHMARK CONTROLLER TEST PASSED")


def test_benchmark_rejects_empty_task():
    try:
        run_benchmark("", "assert True")
    except ValueError as error:
        assert str(error) == "Benchmark task cannot be empty."
    else:
        raise AssertionError("Expected ValueError for empty task.")
