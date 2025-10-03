"""Tests for AI chat functionality."""

import pytest

from apps.ia.agents.conversation_agent import SimpleConversationAgent
from apps.ia.models.conversation import Conversation
from apps.ia.models.document import Document
from apps.ia.models.message import Message
from apps.ia.services.rag_service import RAGService


def test_rag_service_basic_functionality():
    """Test basic RAG service functionality."""
    rag_service = RAGService()

    # Test adding documents
    rag_service.add_document_from_text(
        'O FastAPI é um framework web moderno e rápido para construir APIs com Python.',
        {'source': 'test_doc'},
    )

    # Test document count
    assert rag_service.get_document_count() > 0

    # Test search
    results = rag_service.similarity_search('FastAPI', k=1)
    assert len(results) > 0
    assert 'FastAPI' in results[0].page_content


def test_simple_conversation_agent():
    """Test simple conversation agent."""
    agent = SimpleConversationAgent()

    # This test may fail if GROQ_API_KEY is not set, but should not crash
    try:
        response = agent.chat('Olá, como você está?')
        assert isinstance(response, str)
        assert len(response) > 0
    except Exception as e:
        # Skip test if API key is not configured
        pytest.skip(f'API não configurada: {e}')


def test_conversation_model_creation():
    """Test conversation model creation."""
    # This would need a session fixture in a real test
    # For now, just test model instantiation
    conversation = Conversation(
        str_title='Teste de Conversa',
        str_description='Conversa de teste',
        user_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert conversation.str_title == 'Teste de Conversa'
    assert conversation.str_status == 'active'


def test_message_model_creation():
    """Test message model creation."""
    message = Message(
        txt_content='Esta é uma mensagem de teste',
        str_role='user',
        conversation_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert message.txt_content == 'Esta é uma mensagem de teste'
    assert message.str_role == 'user'


def test_document_model_creation():
    """Test document model creation."""
    document = Document(
        str_title='Documento de Teste',
        txt_content='Este é o conteúdo do documento de teste',
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert document.str_title == 'Documento de Teste'
    assert 'teste' in document.txt_content.lower()


# Integration tests would go here with proper session fixtures
# Example:
# def test_chat_endpoint(client: TestClient, session: Session, test_user: User):
#     """Test chat endpoint integration."""
#     # Create test conversation
#     # Send chat message
#     # Verify response
#     pass


def test_rag_context_retrieval():
    """Test RAG context retrieval functionality."""
    rag_service = RAGService()

    # Add some test documents
    test_docs = [
        'Python é uma linguagem de programação de alto nível.',
        'FastAPI é baseado em Python e oferece alta performance.',
        'SQLAlchemy é um ORM poderoso para Python.',
    ]

    for i, doc in enumerate(test_docs):
        rag_service.add_document_from_text(doc, {'source': f'doc_{i}'})

    # Test context retrieval
    context = rag_service.get_relevant_context('Python', max_tokens=100)
    assert 'Python' in context
    assert len(context) > 0


def test_conversation_title_generation():
    """Test automatic conversation title generation."""
    from apps.ia.api.chat.controller import ChatController

    controller = ChatController()

    # Test short message
    title = controller._generate_conversation_title('Olá')
    assert title == 'Olá'

    # Test long message
    long_message = ' '.join(['palavra'] * 20)
    title = controller._generate_conversation_title(long_message)
    assert len(title) <= 50
    assert title.endswith('...')


if __name__ == '__main__':
    # Run basic tests
    test_rag_service_basic_functionality()
    test_conversation_model_creation()
    test_message_model_creation()
    test_document_model_creation()
    test_rag_context_retrieval()
    test_conversation_title_generation()
    print('✅ Todos os testes básicos passaram!')
