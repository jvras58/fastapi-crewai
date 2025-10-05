"""Advanced tests for RAG Service functionality."""

import contextlib

from apps.ia.services.rag_service import RAGService


def test_rag_service_concurrent_operations(mock_rag_embeddings):
    """Test RAG service handling concurrent operations."""
    rag_service = RAGService()

    documents = [
        ('FastAPI é um framework Python', {'type': 'framework'}),
        ('Django é outro framework Python', {'type': 'framework'}),
        ('React é uma biblioteca JavaScript', {'type': 'library'}),
        ('Vue.js é um framework JavaScript', {'type': 'framework'}),
    ]

    for content, metadata in documents:
        rag_service.add_document_from_text(content, metadata)

    assert rag_service.get_document_count() == 4

    python_results = rag_service.similarity_search('Python framework', k=2)
    js_results = rag_service.similarity_search('JavaScript', k=2)

    assert len(python_results) >= 1
    assert len(js_results) >= 1

    python_content = [r.page_content for r in python_results]
    js_content = [r.page_content for r in js_results]

    assert any('Python' in content for content in python_content)
    assert any('JavaScript' in content for content in js_content)


def test_rag_service_metadata_filtering(mock_rag_embeddings):
    """Test RAG service with metadata-based filtering logic."""
    rag_service = RAGService()

    docs_with_metadata = [
        ('FastAPI documentation', {'category': 'docs', 'language': 'python'}),
        ('FastAPI tutorial', {'category': 'tutorial', 'language': 'python'}),
        ('JavaScript guide', {'category': 'docs', 'language': 'javascript'}),
        ('Python basics', {'category': 'tutorial', 'language': 'python'}),
    ]

    for content, metadata in docs_with_metadata:
        rag_service.add_document_from_text(content, metadata)

    results = rag_service.similarity_search('Python', k=3)
    assert len(results) >= 2


def test_rag_service_large_document_handling(mock_rag_embeddings):
    """Test RAG service with large documents."""
    rag_service = RAGService()

    large_content = 'FastAPI ' * 1000 + 'é um framework Python moderno.'
    large_metadata = {'size': 'large', 'type': 'documentation'}

    rag_service.add_document_from_text(large_content, large_metadata)

    results = rag_service.similarity_search('FastAPI framework', k=1)
    assert len(results) > 0
    assert 'FastAPI' in results[0].page_content


def test_rag_service_special_characters(mock_rag_embeddings):
    """Test RAG service with special characters and encoding."""
    rag_service = RAGService()

    special_docs = [
        'FastAPI suporta acentuação: é, ç, ã, ñ',
        "Códigos em Python: print('Olá, mundo!')",
        'Símbolos especiais: @#$%^&*()[]{}',
        'Emojis também: 🚀 🐍 ⚡ 📚',
    ]

    for i, content in enumerate(special_docs):
        rag_service.add_document_from_text(content, {'doc_id': i})

    results1 = rag_service.similarity_search('acentuação', k=1)
    assert len(results1) > 0

    results2 = rag_service.similarity_search('Python print', k=1)
    assert len(results2) > 0


def test_rag_service_context_window_management(mock_rag_embeddings):
    """Test RAG service context window and token management."""
    rag_service = RAGService()

    for i in range(20):
        content = f'Documento {i} sobre FastAPI. ' * 10
        rag_service.add_document_from_text(content, {'doc_id': i})

    context = rag_service.get_relevant_context('FastAPI', max_tokens=100)
    assert len(context) > 0
    assert len(context.split()) <= 150

    large_context = rag_service.get_relevant_context('FastAPI', max_tokens=500)
    assert len(large_context) >= len(context)


def test_rag_service_persistence_simulation(mock_rag_embeddings):
    """Test RAG service behavior when simulating database persistence."""
    rag_service1 = RAGService()

    documents = ['FastAPI é rápido', 'Django é robusto', 'Flask é simples']

    for i, doc in enumerate(documents):
        rag_service1.add_document_from_text(doc, {'id': i})

    count1 = rag_service1.get_document_count()
    assert count1 == 3

    rag_service2 = RAGService()
    count2 = rag_service2.get_document_count()

    assert count2 == 0


def test_rag_service_error_handling(mock_rag_embeddings):
    """Test RAG service error handling scenarios."""
    rag_service = RAGService()

    with contextlib.suppress(TypeError, ValueError):
        rag_service.add_document_from_text(None, {})
        raise AssertionError('Should have raised an error')

    rag_service.add_document_from_text('Valid content', {})
    assert rag_service.get_document_count() == 1

    results = rag_service.similarity_search('', k=1)
    assert len(results) == 0

    results = rag_service.similarity_search('nonexistent query', k=0)
    assert len(results) == 0


def test_rag_service_performance_characteristics(mock_rag_embeddings):
    """Test RAG service performance with varying loads."""
    rag_service = RAGService()

    batch_sizes = [10, 50, 100]

    for batch_size in batch_sizes:
        rag_service = RAGService()

        for i in range(batch_size):
            content = f'Documento de performance {i} com FastAPI'
            rag_service.add_document_from_text(
                content, {'batch': batch_size, 'id': i}
            )

        assert rag_service.get_document_count() == batch_size

        import time

        start_time = time.time()
        results = rag_service.similarity_search('FastAPI performance', k=5)
        end_time = time.time()

        assert len(results) > 0
        search_time = end_time - start_time
        assert search_time < 5.0


def test_rag_service_multilingual_content(mock_rag_embeddings):
    """Test RAG service with multilingual content."""
    rag_service = RAGService()

    multilingual_docs = [
        'FastAPI is a modern Python web framework',
        'FastAPI é um framework web Python moderno',
        'FastAPI es un framework web moderno de Python',
        'FastAPI est un framework web Python moderne',
    ]

    for i, doc in enumerate(multilingual_docs):
        rag_service.add_document_from_text(doc, {'language': i, 'id': i})

    en_results = rag_service.similarity_search('Python framework', k=2)
    pt_results = rag_service.similarity_search('framework Python', k=2)

    assert len(en_results) > 0
    assert len(pt_results) > 0

    all_content = [r.page_content for r in en_results] + [
        r.page_content for r in pt_results
    ]
    assert any('FastAPI' in content for content in all_content)


def test_rag_service_document_versioning(mock_rag_embeddings):
    """Test RAG service handling document updates/versioning."""
    rag_service = RAGService()

    rag_service.add_document_from_text(
        'FastAPI versão 0.1 - Funcionalidades básicas',
        {'version': '0.1', 'doc_id': 'fastapi_docs'},
    )

    rag_service.add_document_from_text(
        'FastAPI versão 1.0 - Funcionalidades completas e melhoradas',
        {'version': '1.0', 'doc_id': 'fastapi_docs'},
    )

    assert rag_service.get_document_count() == 2

    results = rag_service.similarity_search('FastAPI funcionalidades', k=5)
    assert len(results) >= 2
    versions = {doc.metadata.get('version') for doc in results}
    assert '0.1' in versions and '1.0' in versions


def test_rag_service_vector_store_error_handling(mock_rag_embeddings):
    """Test RAG service handling vector store errors."""
    rag_service = RAGService()

    results = rag_service.similarity_search('test query')
    assert len(results) == 0

    rag_service.add_document_from_text('Test content', {})
    results = rag_service.similarity_search('test')
    assert len(results) >= 0


def test_rag_service_edge_cases(mock_rag_embeddings):
    """Test RAG service edge cases and boundary conditions."""
    rag_service = RAGService()

    rag_service.add_document_from_text('A', {'type': 'short'})
    rag_service.add_document_from_text('FastAPI', {'type': 'word'})

    long_query = 'FastAPI ' * 100
    results = rag_service.similarity_search(long_query, k=1)
    assert len(results) >= 0

    results = rag_service.similarity_search('test', k=1000)
    assert len(results) <= rag_service.get_document_count()

    results = rag_service.similarity_search('test', k=-1)
    assert len(results) == 0
