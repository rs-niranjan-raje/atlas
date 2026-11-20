"""Module 0 check: the Gemini API key in .env works. Run: uv run python scripts/check_gemini.py"""

from dotenv import load_dotenv
from google import genai

MODEL = "gemini-3.5-flash-lite"


def main() -> None:
    load_dotenv()
    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    response = client.models.generate_content(
        model=MODEL, contents="Reply with exactly: Atlas is connected."
    )
    print(f"Model: {MODEL}")
    print(f"Reply: {response.text.strip()}")
    usage = response.usage_metadata
    print(f"Tokens in/out: {usage.prompt_token_count}/{usage.candidates_token_count}")


if __name__ == "__main__":
    main()
