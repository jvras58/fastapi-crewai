"""Project settings, including LLM configuration with Groq."""

from functools import lru_cache

from crewai import LLM
from transformers import pipeline

from apps.packpage.settings import get_settings


@lru_cache(maxsize=1)
def get_llm(use_local_fallback: bool = False):
    """Returns the LLM configured with Groq or local fallback."""
    settings = get_settings()
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in settings")

    if use_local_fallback:
        return pipeline("text-generation", model="microsoft/phi-2", device="cpu")

    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.7,
    )
    return llm
