from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, validate_config


def get_gemini_client():
    """Create an authenticated Gemini client."""
    validate_config()
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_text(
    prompt: str,
    system_instruction: str = None,
):
    """Generate text through Gemini's Interactions API."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client()

    request = {
        "model": GEMINI_MODEL,
        "input": prompt,
    }

    if system_instruction:
        request["system_instruction"] = system_instruction

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


def test_connection():
    """Verify the Gemini API connection."""

    return generate_text(
        prompt="Reply with exactly this text: AGENTGAUGE_CONNECTED"
    )
