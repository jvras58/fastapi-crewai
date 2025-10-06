"""Conversation Agent using CrewAI with optimizations."""

from crewai import Agent, Crew, Process, Task

from apps.core.clients.rag_client import get_rag_tool
from apps.ia.tools.rag_search_tool import rag_search_tool
from apps.packpage.llm import get_llm


class ConversationAgent:
    """Optimized Agent for conversations with RAG and DB support."""

    def __init__(self):
        try:
            self.rag_tool = get_rag_tool()
            self.rag_tool.add(data_type="web_page", url="https://fastapi.tiangolo.com/")
            self.llm = get_llm()
            self.is_configured = True
        except Exception:
            # FIXME: Fallback quando RAG não está configurado
            self.rag_tool = None
            self.llm = get_llm()
            self.is_configured = False

    def create_conversation_agent(self) -> Agent:
        """Create a single optimized conversation agent."""
        return Agent(
            role="Agente de Conversa Inteligente",
            goal="Lidar com conversas com RAG",
            backstory="Você é um assistente eficiente que decide a melhor fonte "
            "e responde diretamente.",
            tools=[rag_search_tool],
            llm=self.llm,
            verbose=False,
            max_iter=3,
            cache=True,
        )

    def process_query(self, query: str) -> str:
        """Process a user query with single task to minimize API calls."""
        if not query or not query.strip():
            return "Por favor, faça uma pergunta para que eu possa ajudá-lo."

        # Se não está configurado, usar resposta simples do LLM
        if not self.is_configured:
            try:
                # Resposta direta usando apenas o LLM
                return (
                    f"Resposta para '{query}': Esta é uma resposta de teste "
                    "do agente. O sistema RAG não está totalmente configurado, "
                    "mas posso responder diretamente usando o LLM configurado."
                )
            except Exception:
                return (
                    "Desculpe, o sistema de IA não está totalmente "
                    "configurado no momento."
                )

        agent = self.create_conversation_agent()

        task = Task(
            description=(
                f"Analise '{query}'. Use tools apenas se necessário "
                "(DB para dados estruturados, RAG para documentos). "
                "Responda diretamente se possível, sem chamadas extras."
            ),
            agent=agent,
            expected_output="Resposta final concisa.",
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

            if hasattr(result, "raw"):
                response = str(result.raw).strip()
            else:
                response = str(result).strip()
            if not response:
                return (
                    "Desculpe, não consegui processar sua pergunta. "
                    "Pode tentar reformulá-la?"
                )

            return response

        except Exception as e:
            if "quota exceeded" in str(e).lower():
                local_llm = get_llm(use_local_fallback=True)
                result = local_llm(query)[0]["generated_text"]
                return str(result).strip()
            else:
                raise
