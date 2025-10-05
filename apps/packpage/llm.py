"""Project settings, including LLM configuration with Groq and caching."""

from functools import lru_cache

import joblib
from crewai import LLM
from langchain_core.caches import InMemoryCache
from transformers import pipeline

from apps.packpage.settings import get_settings

llm_cache = InMemoryCache()
disk_cache = joblib.Memory(location="cache/llm_cache", verbose=0)

def get_llm(use_local_fallback: bool = False):
    """Returns the LLM configured with Groq or local fallback, with caching."""
    settings = get_settings()
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError('GROQ_API_KEY not found in settings')

    if use_local_fallback:
        return pipeline("text-generation", model="microsoft/phi-2", device="cpu")

    @disk_cache.cache
    @lru_cache(maxsize=100)
    def cached_llm(prompt: str):
        llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=api_key,
            temperature=0.7,
        )
        return llm(prompt)

    return cached_llm
