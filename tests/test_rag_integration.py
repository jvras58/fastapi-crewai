"""Tests for RAG integration with conversation agents."""

from unittest.mock import Mock, patch

from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.tools.rag_search_tool import rag_search_function


class TestRAGIntegration:
    """Test RAG integration with conversation agents."""

    def test_rag_search_tool_function(self):
        """Test the RAG search tool function directly."""

        with patch(
            'apps.ia.tools.rag_search_tool.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service

            mock_doc = Mock()
            mock_doc.page_content = 'Este é um conteúdo de teste sobre IA.'
            mock_doc.metadata = {'source': 'documento_teste.pdf'}
            mock_rag_service.similarity_search.return_value = [mock_doc]

            result = rag_search_function('IA artificial')

            mock_rag_service.similarity_search.assert_called_once_with(
                'IA artificial', k=3
            )
            assert 'Este é um conteúdo de teste sobre IA.' in result
            assert 'documento_teste.pdf' in result

    def test_rag_search_tool_no_results(self):
        """Test RAG search tool when no documents are found."""
        with patch(
            'apps.ia.tools.rag_search_tool.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service
            mock_rag_service.similarity_search.return_value = []

            result = rag_search_function('termo inexistente')

            assert 'Nenhuma informação relevante encontrada' in result

    def test_rag_search_tool_error_handling(self):
        """Test RAG search tool error handling."""
        with patch(
            'apps.ia.tools.rag_search_tool.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service
            mock_rag_service.similarity_search.side_effect = Exception(
                'Erro de teste'
            )

            result = rag_search_function('query')

            assert 'Erro ao buscar na base de conhecimento' in result

    def test_conversation_agent_has_rag_tool(self):
        """Test that ConversationAgent has RAG tool configured."""
        with patch('apps.ia.agents.conversation_agent.RAGService'):
            agent = ConversationAgent()

            assert len(agent.agent.tools) > 0

            tool_names = [tool.name for tool in agent.agent.tools]
            assert 'rag_search' in tool_names

    def test_conversation_agent_rag_integration(self):
        """Test complete RAG integration in conversation agent."""
        with patch(
            'apps.ia.agents.conversation_agent.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service
            mock_rag_service.get_relevant_context.return_value = (
                'Contexto RAG de teste'
            )

            with patch(
                'apps.ia.agents.conversation_agent.Crew'
            ) as mock_crew_class:
                mock_crew_instance = Mock()
                mock_crew_class.return_value = mock_crew_instance
                mock_crew_instance.kickoff.return_value = (
                    'Resposta de teste com contexto RAG'
                )

                agent = ConversationAgent(mock_rag_service)
                response = agent.chat('Pergunta sobre documentos')

                mock_rag_service.get_relevant_context.assert_called_once()

                mock_crew_class.assert_called_once()
                mock_crew_instance.kickoff.assert_called_once()

                assert response == 'Resposta de teste com contexto RAG'

    def test_conversation_agent_knowledge_management(self):
        """Test knowledge management methods in ConversationAgent."""
        with patch(
            'apps.ia.agents.conversation_agent.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service

            agent = ConversationAgent(mock_rag_service)

            agent.add_knowledge('Novo conhecimento', {'source': 'teste'})
            mock_rag_service.add_document_from_text.assert_called_once_with(
                'Novo conhecimento', {'source': 'teste'}
            )

            texts = ['Doc 1', 'Doc 2']
            metadatas = [{'source': '1'}, {'source': '2'}]
            agent.add_multiple_documents(texts, metadatas)
            mock_rag_service.add_documents.assert_called_once_with(
                texts, metadatas
            )

            agent.clear_knowledge()
            mock_rag_service.clear_knowledge_base.assert_called_once()

            mock_rag_service.get_document_count.return_value = 5
            mock_rag_service.vector_store = Mock()

            stats = agent.get_knowledge_stats()
            assert stats['document_count'] == 5
            assert stats['has_vector_store'] is True

    def test_conversation_agent_search_knowledge(self):
        """Test direct knowledge search in ConversationAgent."""
        with patch(
            'apps.ia.agents.conversation_agent.RAGService'
        ) as mock_rag_service_class:
            mock_rag_service = Mock()
            mock_rag_service_class.return_value = mock_rag_service

            mock_docs = [Mock(), Mock()]
            mock_rag_service.similarity_search.return_value = mock_docs

            agent = ConversationAgent(mock_rag_service)
            results = agent.search_knowledge('busca teste', k=2)

            mock_rag_service.similarity_search.assert_called_once_with(
                'busca teste', k=2
            )
            assert results == mock_docs
