"""Tests for AI document and RAG functionality."""

from unittest.mock import Mock, patch

import pytest

from apps.ia.api.documents.controller import DocController
from apps.ia.api.documents.schemas import DocumentUploadSchema
from apps.ia.models.document import Document
from apps.ia.services.rag_service import RAGService


def test_rag_service_basic_functionality(mock_rag_embeddings):
    """Test basic RAG service functionality."""
    rag_service = RAGService()

    rag_service.add_document_from_text(
        'O FastAPI é um framework web moderno e rápido para construir APIs com Python.',
        {'source': 'test_doc'},
    )

    assert rag_service.get_document_count() > 0

    results = rag_service.similarity_search('FastAPI', k=1)
    assert len(results) > 0
    assert 'FastAPI' in results[0].page_content


def test_rag_context_retrieval(mock_rag_embeddings):
    """Test RAG context retrieval functionality."""
    rag_service = RAGService()

    test_docs = [
        'Python é uma linguagem de programação de alto nível.',
        'FastAPI é baseado em Python e oferece alta performance.',
        'SQLAlchemy é um ORM poderoso para Python.',
    ]

    for i, doc in enumerate(test_docs):
        rag_service.add_document_from_text(doc, {'source': f'doc_{i}'})

    context = rag_service.get_relevant_context("Python", max_tokens=100)
    assert "Python" in context
    assert len(context) > 0


def test_rag_service_empty_state(mock_rag_embeddings):
    """Test RAG service in empty state."""
    rag_service = RAGService()

    assert rag_service.get_document_count() == 0

    results = rag_service.similarity_search('test', k=1)
    assert len(results) == 0


def test_rag_service_multiple_documents(mock_rag_embeddings):
    """Test RAG service with multiple documents."""
    rag_service = RAGService()

    documents = [
        'FastAPI é um framework moderno para APIs REST.',
        'Python é uma linguagem versátil e poderosa.',
        'SQLAlchemy facilita o trabalho com bancos de dados.',
        'CrewAI permite a criação de agentes inteligentes.',
    ]

    for i, doc in enumerate(documents):
        rag_service.add_document_from_text(doc, {'source': f'multi_doc_{i}'})

    assert rag_service.get_document_count() == len(documents)

    results = rag_service.similarity_search('framework', k=2)
    assert len(results) > 0

    framework_mentioned = any('FastAPI' in result.page_content for result in results)
    assert framework_mentioned


def test_rag_service_search_relevance(mock_rag_embeddings):
    """Test RAG service search relevance scoring."""
    rag_service = RAGService()

    docs = [
        'FastAPI é o melhor framework para Python APIs.',
        'Django também é um framework Python popular.',
        'JavaScript é usado para desenvolvimento frontend.',
    ]

    for i, doc in enumerate(docs):
        rag_service.add_document_from_text(doc, {'source': f'relevance_doc_{i}'})

    results = rag_service.similarity_search('Python framework', k=3)

    assert len(results) > 0

    python_results = [r for r in results if 'Python' in r.page_content]
    assert len(python_results) >= 2


def test_rag_service_advanced_scenarios(mock_rag_embeddings):
    """Test advanced RAG service scenarios."""
    rag_service = RAGService()

    # Test with empty query
    results = rag_service.similarity_search('', k=1)
    assert len(results) == 0

    similar_docs = [
        'FastAPI é um framework Python para APIs.',
        'FastAPI é uma biblioteca Python para criar APIs.',
        'FastAPI ajuda a construir APIs em Python.',
    ]

    for i, doc in enumerate(similar_docs):
        rag_service.add_document_from_text(doc, {'source': f'similar_{i}'})

    results = rag_service.similarity_search('FastAPI Python', k=3)
    assert len(results) == 3

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


def test_document_model_validation():
    """Test document model field validation."""
    document = Document(
        str_title='',
        str_filename='test.txt',
        txt_content='Conteúdo de teste',
        str_content_type='text/plain',
        int_size_bytes=100,
        str_content_hash='abc123',
        str_status='active',
        audit_user_ip='192.168.1.1',
        audit_user_login='admin',
    )

    assert document.txt_content == 'Conteúdo de teste'
    assert document.str_status == 'active'
    assert document.audit_user_ip == '192.168.1.1'
    assert document.audit_user_login == 'admin'
    assert document.str_filename == 'test.txt'
    assert document.str_content_type == 'text/plain'
    assert document.int_size_bytes == 100
    assert document.str_content_hash == 'abc123'


def test_document_model_with_metadata():
    """Test document model with JSON metadata."""
    document = Document(
        str_title='Doc com Metadata',
        txt_content='Conteúdo com metadados',
        json_metadata='{"categoria": "teste", "prioridade": "alta"}',
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert document.json_metadata is not None
    assert 'categoria' in document.json_metadata


def test_doc_controller_initialization():
    """Test document controller initialization."""
    controller = DocController()
    assert controller is not None
    assert hasattr(controller, 'rag_service')
    assert hasattr(controller, 'conversation_agent')


@patch('apps.ia.api.documents.controller.RAGService')
def test_upload_document_success(mock_rag_service, session, user):
    """Test successful document upload."""
    mock_rag = Mock()
    mock_rag_service.return_value = mock_rag

    controller = DocController()
    controller.rag_service = mock_rag

    document_data = DocumentUploadSchema(
        title="Documento de Teste",
        content="Este é o conteúdo do documento de teste para upload.",
        content_type="text/plain",
        filename="test.txt",
        metadata={"source": "test", "category": "example"}
    )

    document = controller.upload_document(session, document_data, user, "127.0.0.1")

    assert document.id is not None
    assert document.str_title == "Documento de Teste"
    assert document.str_filename == "test.txt"
    assert document.str_content_type == "text/plain"
    assert document.str_status == "active"
    assert document.int_size_bytes > 0
    assert document.str_content_hash is not None

    mock_rag.add_document_from_text.assert_called_once()


# @pytest.mark.usefixtures("mock_rag_embeddings")
def test_upload_duplicate_document(session, user, document, mock_rag_embeddings):
    """Test uploading a duplicate document (same content hash)."""
    controller = DocController()

    document_data = DocumentUploadSchema(
        title="Documento Duplicado",
        content="Este é um documento de teste para o sistema de RAG.",
        content_type="text/plain",
        filename="duplicate.txt"
    )

    with pytest.raises(ValueError, match="Documento com este conteúdo já existe"):
        controller.upload_document(session, document_data, user, "127.0.0.1")


def test_get_documents_pagination(session, multiple_documents):
    """Test document pagination."""
    controller = DocController()

    result = controller.get_documents(session, page=1, per_page=5)

    assert 'documents' in result
    assert 'total' in result
    assert 'page' in result
    assert 'per_page' in result

    assert len(result['documents']) <= 5
    assert result['total'] == 10
    assert result['page'] == 1
    assert result['per_page'] == 5

    result_page2 = controller.get_documents(session, page=2, per_page=5)
    assert len(result_page2['documents']) <= 5
    assert result_page2['page'] == 2


@patch('apps.ia.api.documents.controller.RAGService')
def test_search_knowledge_base(mock_rag_service):
    """Test knowledge base search functionality."""
    mock_rag = Mock()
    mock_doc = Mock()
    mock_doc.page_content = "FastAPI é um framework Python"
    mock_doc.metadata = {"source": "test_doc", "doc_id": 1}
    mock_rag.similarity_search.return_value = [mock_doc]
    mock_rag_service.return_value = mock_rag

    controller = DocController()
    controller.rag_service = mock_rag

    results = controller.search_knowledge_base("FastAPI", k=5)

    assert len(results) == 1
    assert results[0]['content'] == "FastAPI é um framework Python"
    assert results[0]['metadata']['source'] == "test_doc"
    assert results[0]['source'] == "test_doc"

    mock_rag.similarity_search.assert_called_once_with("FastAPI", k=5)


def test_search_knowledge_base_empty_results():
    """Test knowledge base search with no results."""
    controller = DocController()

    results = controller.search_knowledge_base("nonexistent", k=5)
    assert len(results) == 0
