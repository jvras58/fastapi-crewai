"""Conversation Agent using CrewAI with optimizations."""

from crewai import Agent, Crew, Process, Task

from apps.ia.services.rag_service import RAGService
from apps.ia.tools.db_query_tool import db_query_tool
from apps.ia.tools.rag_search_tool import rag_search_tool
from apps.packpage.llm import get_llm


class ConversationAgent:
    """Optimized Agent for conversations with RAG and DB support."""

    def __init__(self, rag_service: RAGService = None):
        self.rag_service = rag_service or RAGService()
        self.llm = get_llm()

    def create_conversation_agent(self) -> Agent:
        """Create a single optimized conversation agent."""
        return Agent(
            role='Agente de Conversa Inteligente',
            goal='Responder perguntas usando DB, RAG ou conhecimento geral, '
            'com mínimo de chamadas.',
            backstory='Você é um assistente eficiente que decide a melhor fonte '
            'e responde diretamente.',
            tools=[rag_search_tool, db_query_tool],
            llm=self.llm,
            verbose=False,
            max_iter=3,
        )

    def process_query(self, query: str) -> str:
        """Process a user query with single task to minimize API calls."""
        if not query or not query.strip():
            return 'Por favor, faça uma pergunta para que eu possa ajudá-lo.'

        agent = self.create_conversation_agent()

        task = Task(
            description=(
                f"Analise '{query}'. Use tools apenas se necessário "
                '(DB para dados estruturados, RAG para documentos). '
                'Responda diretamente se possível, sem chamadas extras.'
            ),
            agent=agent,
            expected_output='Resposta final concisa à query.',
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=1,
            cache=True,
        )

        try:
            result = crew.kickoff()

            if hasattr(result, 'raw'):
                response = str(result.raw).strip()
            else:
                response = str(result).strip()
            if not response:
                return (
                    'Desculpe, não consegui processar sua pergunta. '
                    'Pode tentar reformulá-la?'
                )

            return response

        except Exception as e:
            if 'quota exceeded' in str(e).lower():
                local_llm = get_llm(use_local_fallback=True)
                result = local_llm(query)[0]['generated_text']
                return str(result).strip()
            else:
                raise
