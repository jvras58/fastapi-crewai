"""Project settings, including LLM configuration with Groq."""

from crewai import LLM

from apps.utils.settings import get_settings


def get_llm():
    """Returns the LLM configured with Groq using Meta's Llama."""
    settings = get_settings()
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError('GROQ_API_KEY not found in settings')

    return LLM(
        model='groq/llama-3.1-8b-instant',
        api_key=api_key,
        temperature=0.7,  # Creativity control (0-1)
    )
