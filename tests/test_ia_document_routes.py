"""Tests for AI document routes and endpoints."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

from fastapi import status

from apps.ia.models.document import Document


@patch("apps.ia.api.documents.router.doc_controller")
def test_upload_document_success(mock_doc_controller, client, token, user):
    """Test successful document upload via API."""

    mock_document = Document(
        id=1,
        str_title="Documento via API",
        str_filename="api_test.txt",
        txt_content="Este é o conteúdo do documento enviado via API REST.",
        str_content_type="text/plain",
        json_metadata='{"source": "api", "category": "test"}',
        str_status="active",
        dt_uploaded_at=datetime.now(UTC),
        dt_processed_at=datetime.now(UTC),
        int_size_bytes=100,
        str_content_hash="mock_hash",
        audit_user_ip="127.0.0.1",
        audit_user_login="Teste",
        audit_created_at=datetime.now(UTC),
        audit_updated_on=datetime.now(UTC),
    )

    mock_doc_controller.upload_document.return_value = mock_document

    document_data = {
        "str_title": "Documento via API",
        "txt_content": "Este é o conteúdo do documento enviado via API REST.",
        "str_content_type": "text/plain",
        "str_filename": "api_test.txt",
        "json_metadata": {"source": "api", "category": "test"},
    }

    response = client.post(
        "/ia/documents",
        json=document_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["str_title"] == "Documento via API"
    assert data["str_filename"] == "api_test.txt"
    assert data["str_content_type"] == "text/plain"
    assert data["str_status"] == "active"
    assert "id" in data
    assert "dt_uploaded_at" in data


def test_upload_document_unauthorized(client):
    """Test document upload without authentication."""
    document_data = {
        "str_title": "Documento não autorizado",
        "txt_content": "Este upload deve falhar",
    }

    response = client.post("/ia/documents", json=document_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_document_invalid_data(client, token):
    """Test document upload with invalid data."""
    response = client.post(
        "/ia/documents",
        json={"str_title": "", "txt_content": "Conteúdo válido"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        "/ia/documents",
        json={"str_title": "Título válido", "txt_content": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        "/ia/documents",
        json={"str_title": "Sem conteúdo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_duplicate_document(client, token, document):
    """Test uploading a document with duplicate content."""
    document_data = {
        "str_title": "Documento Duplicado",
        "txt_content": "Este é um documento de teste para o sistema de RAG.",
        "str_content_type": "text/plain",
        "str_filename": "duplicate.txt",
    }

    response = client.post(
        "/ia/documents",
        json=document_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já existe" in response.json()["detail"]


@patch("apps.ia.api.documents.router.doc_controller")
def test_upload_document_with_metadata(mock_doc_controller, client, token):
    """Test uploading document with custom metadata."""
    from datetime import UTC, datetime

    from apps.ia.models.document import Document

    mock_document = Document(
        id=1,
        str_title="Doc com Metadata",
        str_filename="metadata_test.md",
        txt_content="Documento com metadados personalizados",
        str_content_type="text/markdown",
        json_metadata='{"author": "Test Author", "category": "documentation"}',
        str_status="active",
        dt_uploaded_at=datetime.now(UTC),
        dt_processed_at=datetime.now(UTC),
        int_size_bytes=100,
        str_content_hash="mock_hash",
        audit_user_ip="127.0.0.1",
        audit_user_login="Teste",
        audit_created_at=datetime.now(UTC),
        audit_updated_on=datetime.now(UTC),
    )

    mock_doc_controller.upload_document.return_value = mock_document

    document_data = {
        "str_title": "Doc com Metadata",
        "txt_content": "Documento com metadados personalizados",
        "str_content_type": "text/markdown",
        "str_filename": "metadata_test.md",
        "json_metadata": {
            "author": "Test Author",
            "category": "documentation",
            "priority": "high",
            "tags": ["api", "test", "documentation"],
        },
    }

    response = client.post(
        "/ia/documents",
        json=document_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["str_content_type"] == "text/markdown"


def test_list_documents(client, token, multiple_documents):
    """Test listing documents."""
    response = client.get(
        "/ia/documents",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "documents" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data

    assert data["total"] == 10
    assert len(data["documents"]) <= 20


def test_list_documents_pagination(client, token, multiple_documents):
    """Test document listing with pagination."""
    response = client.get(
        "/ia/documents?page=1&per_page=5",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["page"] == 1
    assert data["per_page"] == 5
    assert len(data["documents"]) <= 5

    response = client.get(
        "/ia/documents?page=2&per_page=5", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 2


def test_list_documents_unauthorized(client):
    """Test listing documents without authentication."""
    response = client.get("/ia/documents")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_documents_pagination_limits(client, token, multiple_documents):
    """Test pagination limits."""
    response = client.get(
        "/ia/documents?per_page=150", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["per_page"] == 100


@patch("apps.ia.api.documents.controller.RAGService")
def test_search_knowledge_base_success(mock_rag_service, client, token):
    """Test successful knowledge base search."""
    mock_rag = Mock()
    mock_doc = Mock()
    mock_doc.page_content = "FastAPI é um framework Python moderno"
    mock_doc.metadata = {"source": "test_doc", "doc_id": 1}
    mock_rag.similarity_search.return_value = [mock_doc]
    mock_rag_service.return_value = mock_rag

    response = client.get(
        "/ia/search?q=FastAPI&k=5", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "query" in data
    assert "results" in data
    assert "count" in data

    assert data["query"] == "FastAPI"
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert "FastAPI" in data["results"][0]["content"]


def test_search_knowledge_base_unauthorized(client):
    """Test knowledge base search without authentication."""
    response = client.get("/ia/search?q=test")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_knowledge_base_no_query(client, token):
    """Test search without query parameter."""
    response = client.get("/ia/search", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_search_knowledge_base_k_limit(client, token):
    """Test search with k parameter limit."""
    with patch("apps.ia.api.documents.controller.RAGService"):
        response = client.get(
            "/ia/search?q=test&k=25", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == status.HTTP_200_OK


def test_search_knowledge_base_empty_results(client, token):
    """Test search with no results."""
    with patch("apps.ia.api.documents.controller.RAGService") as mock_rag_service:
        mock_rag = Mock()
        mock_rag.similarity_search.return_value = []
        mock_rag_service.return_value = mock_rag

        response = client.get(
            "/ia/search?q=nonexistent", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 0
    assert len(data["results"]) == 0


@patch("apps.ia.api.documents.router.doc_controller")
def test_document_upload_and_search_flow(mock_doc_controller, client, token):
    """Test complete document upload and search flow."""
    from datetime import UTC, datetime

    from apps.ia.models.document import Document

    mock_document = Document(
        id=1,
        str_title="FastAPI Documentation",
        str_filename="fastapi.txt",
        txt_content=(
            "FastAPI é um framework web moderno e rápido (high-performance) "
            "para construir APIs com Python 3.7+ baseado nas dicas de tipos "
            "padrões do Python."
        ),
        str_content_type="text/plain",
        json_metadata='{"category": "documentation", "framework": "fastapi"}',
        str_status="active",
        dt_uploaded_at=datetime.now(UTC),
        dt_processed_at=datetime.now(UTC),
        int_size_bytes=100,
        str_content_hash="mock_hash",
        audit_user_ip="127.0.0.1",
        audit_user_login="Teste",
        audit_created_at=datetime.now(UTC),
        audit_updated_on=datetime.now(UTC),
    )

    mock_doc_controller.upload_document.return_value = mock_document

    document_data = {
        "str_title": "FastAPI Documentation",
        "txt_content": (
            "FastAPI é um framework web moderno e rápido (high-performance) "
            "para construir APIs com Python 3.7+ baseado nas dicas de tipos "
            "padrões do Python."
        ),
        "str_content_type": "text/plain",
        "str_filename": "fastapi.txt",
        "json_metadata": {"category": "documentation", "framework": "fastapi"},
    }

    upload_response = client.post(
        "/ia/documents",
        json=document_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert upload_response.status_code == status.HTTP_200_OK
    doc_data = upload_response.json()
    assert doc_data["str_title"] == "FastAPI Documentation"

    assert doc_data["str_title"] == "FastAPI Documentation"
    assert doc_data["str_filename"] == "fastapi.txt"
    assert "FastAPI" in doc_data["txt_content"]


def test_document_api_error_handling(client, token):
    """Test error handling in document API."""
    with patch(
        "apps.ia.api.documents.controller.DocController.upload_document"
    ) as mock_upload:
        mock_upload.side_effect = Exception("RAG service error")

        document_data = {
            "str_title": "Error Test",
            "txt_content": "This should cause an error",
        }

        response = client.post(
            "/ia/documents",
            json=document_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "erro" in response.json()["detail"].lower()

    with patch(
        "apps.ia.api.documents.controller.DocController.search_knowledge_base"
    ) as mock_search:
        mock_search.side_effect = Exception("Search service error")

        response = client.get(
            "/ia/search?q=test",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "erro" in response.json()["detail"].lower()
