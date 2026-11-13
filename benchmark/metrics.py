def build_comparison(direct_result: dict, verify_result: dict) -> dict:
    """Build a side-by-side comparison using actual benchmark results."""

    direct_tests = direct_result["test_result"]
    verify_tests = verify_result["test_result"]

    metrics = [
        {
            "metric": "Correctness",
            "direct_coder": direct_tests["passed"],
            "verify_coder": verify_tests["passed"],
            "unit": "passed",
        },
        {
            "metric": "Latency",
            "direct_coder": direct_result["latency_seconds"],
            "verify_coder": verify_result["latency_seconds"],
            "unit": "seconds",
        },
        {
            "metric": "Total tokens",
            "direct_coder": direct_result["total_tokens"],
            "verify_coder": verify_result["total_tokens"],
            "unit": "tokens",
        },
        {
            "metric": "Correction attempts",
            "direct_coder": direct_result["attempts"],
            "verify_coder": verify_result["attempts"],
            "unit": "attempts",
        },
        {
            "metric": "Test execution time",
            "direct_coder": direct_result["test_latency_seconds"],
            "verify_coder": verify_result["test_latency_seconds"],
            "unit": "seconds",
        },
    ]

    return {
        "metrics": metrics,
        "direct_coder_success": direct_tests["passed"],
        "verify_coder_success": verify_tests["passed"],
    }
