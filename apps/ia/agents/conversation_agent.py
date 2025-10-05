"""Conversation Agent using CrewAI for intelligent chat interactions."""

from typing import Any

from crewai import Agent, Crew, Task
from langchain.schema import Document

from apps.ia.services.rag_service import RAGService
from apps.ia.tools.rag_search_tool import RAGSearchTool, rag_search_tool
from apps.packpage.llm import get_llm


class ConversationAgent:
    """Agent for handling conversational interactions with RAG context."""

    def __init__(self, rag_service: RAGService | None = None):
        """Initialize the conversation agent."""
        self.llm = get_llm()
        self.rag_service = rag_service or RAGService()
        self.rag_tool = RAGSearchTool(self.rag_service)
        self._setup_agent()

    def _setup_agent(self) -> None:
        """Setup the CrewAI agent with tools and configuration."""
        self.agent = Agent(
            role="Assistente Conversacional Inteligente",
            goal="""Fornecer respostas precisas e úteis baseadas no conhecimento
                    disponível e na conversa em andamento. Usar o contexto do RAG
                    quando relevante para enriquecer as respostas.""",
            backstory="""Você é um assistente AI especializado em conversação
                        natural e busca de informações. Você tem acesso a uma
                        base de conhecimento através de RAG (Retrieval Augmented
                        Generation) e pode usar a ferramenta 'rag_search' para
                        buscar informações relevantes nos documentos enviados.
                        SEMPRE use a ferramenta rag_search quando o usuário fizer
                        perguntas que possam estar relacionadas aos documentos
                        da base de conhecimento.""",
            # tools=[], -- Use this line to disable the RAG tool
            tools=[rag_search_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def chat(self, message: str, context: str = '') -> str:
        """Process a chat message and return a response."""
        # Buscar contexto relevante no RAG
        rag_context = self.rag_service.get_relevant_context(
            message, max_tokens=1500
        )

        # Combinar contextos
        full_context = context
        if rag_context:
            full_context += (
                f'\n\nInformações da base de conhecimento:\n{rag_context}'
            )

        # Criar tarefa para o agent
        task = Task(
            description=f"""
            Processar a seguinte mensagem do usuário e fornecer uma resposta útil:
            Mensagem do usuário: {message}
            Contexto disponível: {full_context}
            Instruções:
            1. Analise a mensagem do usuário
            2. Se a pergunta puder estar relacionada a documentos ou informações
               específicas, USE A FERRAMENTA 'rag_search' para buscar informações
               relevantes na base de conhecimento
            3. Use as informações do contexto e dos resultados do rag_search
            4. Forneça uma resposta clara, útil e baseada em evidências
            5. Mantenha um tom conversacional e amigável
            6. Se não tiver informações suficientes, seja honesto sobre limitações
            7. Sempre cite as fontes quando usar informações da base de conhecimento
            """,
            agent=self.agent,
            expected_output="""Uma resposta conversacional clara e útil que aborde
                            a pergunta do usuário, utilizando informações do contexto
                            quando relevantes.""",
        )

        # Executar a tarefa
        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

        result = crew.kickoff()
        return str(result)

    def add_knowledge(
        self, text: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Add knowledge to the RAG service."""
        self.rag_service.add_document_from_text(text, metadata)

    def add_multiple_documents(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> None:
        """Add multiple documents to the knowledge base."""
        self.rag_service.add_documents(texts, metadatas)

    def clear_knowledge(self) -> None:
        """Clear the knowledge base."""
        self.rag_service.clear_knowledge_base()

    def get_knowledge_stats(self) -> dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            'document_count': self.rag_service.get_document_count(),
            'has_vector_store': self.rag_service.vector_store is not None,
        }

    def search_knowledge(self, query: str, k: int = 3) -> list[Document]:
        """Search the knowledge base directly."""
        return self.rag_service.similarity_search(query, k=k)


class SimpleConversationAgent:
    """Simplified conversation agent for direct LLM interaction."""

    def __init__(self):
        """Initialize simple conversation agent."""
        self.llm = get_llm()
        self._setup_agent()

    def _setup_agent(self) -> None:
        """Setup simple agent without RAG tools."""
        self.agent = Agent(
            role='Assistente Conversacional',
            goal='Fornecer respostas úteis e claras para as perguntas dos usuários',
            backstory="""Você é um assistente AI amigável e prestativo que
                        responde perguntas de forma clara e concisa.""",
            tools=[],
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

    def chat(self, message: str) -> str:
        """Process a simple chat message."""
        task = Task(
            description=f"""
            Responda à seguinte pergunta de forma clara e útil:
            Pergunta: {message}
            Forneça uma resposta direta, informativa e amigável.
            """,
            agent=self.agent,
            expected_output='Uma resposta clara e útil para a pergunta do usuário.',
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=False)

        result = crew.kickoff()
        return str(result)
