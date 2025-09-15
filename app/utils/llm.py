"""Configurações do projeto, incluindo a configuração do LLM com Groq."""

from crewai import LLM

from app.utils.settings import get_settings


def get_llm():
    """Retorna o LLM configurado com Groq usando Llama da Meta."""
    settings = get_settings()
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError('GROQ_API_KEY não encontrada nas configurações')

    return LLM(
        model='groq/llama-3.1-8b-instant',
        api_key=api_key,
        temperature=0.7,  # Controle de criatividade (0-1)
    )
