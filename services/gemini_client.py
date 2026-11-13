import time

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, validate_config


def get_gemini_client():
    validate_config()
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_text(
    prompt: str,
    system_instruction: str = None,
    max_retries: int = 2,
):
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client()

    request = {
        "model": GEMINI_MODEL,
        "input": prompt,
    }

    if system_instruction:
        request["system_instruction"] = system_instruction

    for attempt in range(max_retries + 1):
        try:
            interaction = client.interactions.create(**request)

            generated_text = interaction.output_text

            if not generated_text:
                raise RuntimeError("Gemini returned an empty response.")

            usage = interaction.usage

            return {
                "text": generated_text,
                "model": GEMINI_MODEL,
                "prompt_tokens": getattr(
                    usage, "total_input_tokens", None
                ) if usage else None,
                "completion_tokens": getattr(
                    usage, "total_output_tokens", None
                ) if usage else None,
                "total_tokens": getattr(
                    usage, "total_tokens", None
                ) if usage else None,
                "thought_tokens": getattr(
                    usage, "total_thought_tokens", None
                ) if usage else None,
            }

        except Exception as error:
            message = str(error).lower()

            transient = any(
                marker in message
                for marker in (
                    "503",
                    "502",
                    "504",
                    "429",
                    "service_unavailable",
                    "high demand",
                    "resource_exhausted",
                    "temporarily unavailable",
                )
            )

            if not transient or attempt >= max_retries:
                raise

            wait_seconds = 3 * (attempt + 1)

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds "
                f"({attempt + 1}/{max_retries})..."
            )

            time.sleep(wait_seconds)


def test_connection():
    return generate_text(
        prompt="Reply with exactly this text: AGENTGAUGE_CONNECTED"
    )