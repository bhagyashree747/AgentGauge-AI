import time

from services.gemini_client import generate_text


SYSTEM_INSTRUCTION = """
You are DirectCoder, a Python coding agent.

Your job is to solve programming tasks accurately.

Rules:
1. Return a complete Python solution.
2. Follow all requirements in the user's task.
3. Use clear variable and function names.
4. Handle relevant edge cases.
5. Do not include explanations outside the code.
6. Do not include Markdown code fences.
7. Do not fabricate test results.
"""


def clean_code(response: str) -> str:
    """Remove Markdown code fences if Gemini includes them."""

    code = response.strip()

    if code.startswith("```"):
        lines = code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    return code


def run_direct_coder(task: str) -> dict:
    """
    Generate a Python solution using a single Gemini request.

    Returns generated code and execution metadata.
    """

    if not task or not task.strip():
        raise ValueError("Coding task cannot be empty.")

    start_time = time.perf_counter()

    result = generate_text(
        prompt=(
            "Solve the following programming task using Python.\n\n"
            f"PROGRAMMING TASK:\n{task}\n\n"
            "Return only the complete Python source code."
        ),
        system_instruction=SYSTEM_INSTRUCTION,
    )

    latency = time.perf_counter() - start_time

    code = clean_code(result["text"])

    if not code:
        raise RuntimeError("DirectCoder generated empty code.")

    return {
        "agent": "DirectCoder",
        "code": code,
        "model": result["model"],
        "latency_seconds": round(latency, 3),
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
        "total_tokens": result["total_tokens"],
        "thought_tokens": result["thought_tokens"],
        "attempts": 1,
        "success": True,
    }
