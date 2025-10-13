"""Módulo para construção de prompts de agentes."""

import os

from apps.ia.utils.load_yaml import load_agent_prompt


def build_agent_prompt_conversation_agent(prompt_path: str = None) -> dict:
    """Constrói o prompt completo do agente de conversa,
    integrando exemplos no backstory."""
    if prompt_path is None:
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            'conversation_agent_prompt.yaml',
        )
    prompt = load_agent_prompt(prompt_path)

    backstory_base = prompt.get(
        'backstory', 'Especialista em conversação com contexto mantido.'
    )
    examples = prompt.get('examples', [])
    if examples:
        backstory_base += '\n\nExemplos de respostas:\n'
        for ex in examples:
            backstory_base += (
                f"- Pergunta: {ex['question']}\n  Resposta: {ex['answer']}\n"
            )
    prompt['backstory'] = backstory_base
    return prompt
