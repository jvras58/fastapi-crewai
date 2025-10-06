"""RAG (Retrieval Augmented Generation) Service using LangChain."""

import logging
import os
from typing import Any
from uuid import uuid4

import numpy as np
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from apps.packpage.settings import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for document processing, embedding and semantic search using RAG."""

    def __init__(self):
        """Initialize RAG service with embeddings and vector store."""
        self.settings = get_settings()
        self.embeddings = self._setup_embeddings()
        self.vector_store: FAISS | None = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents: list[Document] = []

    def _setup_embeddings(self) -> Embeddings:
        """Setup local HuggingFace embeddings."""
        try:
            return HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={'device': 'cpu'},
            )
        except Exception as e:
            logger.error(f'Falha ao configurar embeddings locais: {str(e)}')
            logger.warning(
                f'Falha ao configurar HuggingFace embeddings: {str(e)}, '
                'usando fallback simples'
            )

            # TODO: Refatorar testes para usar embeddings simples e não mocks
            class SimpleEmbeddings(Embeddings):
                def embed_documents(
                    self, texts: list[str]
                ) -> list[list[float]]:
                    return [self._simple_embed(text) for text in texts]

                def embed_query(self, text: str) -> list[float]:
                    return self._simple_embed(text)

                def _simple_embed(self, text: str) -> list[float]:
                    hash_val = hash(text.lower())
                    np.random.seed(abs(hash_val) % (2**31))
                    return np.random.normal(0, 1, 384).tolist()

            return SimpleEmbeddings()

    def add_documents(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> None:
        """Add documents to the RAG knowledge base."""
        try:
            if metadatas is None:
                metadatas = [{'source': f'doc_{uuid4()}'} for _ in texts]

            valid_docs = []
            valid_metadatas = []

            for text, metadata in zip(texts, metadatas, strict=True):
                if text is None or not str(text).strip():
                    logger.warning(f'Skipping invalid document: {text}')
                    continue

                valid_docs.append(str(text))
                valid_metadatas.append(metadata)

            if not valid_docs:
                logger.warning('No valid documents to add')
                return

            documents = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(
                    valid_docs, valid_metadatas, strict=True
                )
            ]

            chunked_docs = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                chunked_docs.extend(chunks)

            self.documents.extend(chunked_docs)

            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(
                    chunked_docs, self.embeddings
                )
            else:
                self.vector_store.add_documents(chunked_docs)

        except Exception as e:
            logger.error(
                f'Erro ao adicionar documentos ao RAG: {str(e)}', exc_info=True
            )

    def add_document_from_text(
        self, text: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Add a single document from text."""
        if metadata is None:
            metadata = {'source': f'doc_{uuid4()}'}

        self.add_documents([text], [metadata])

    def similarity_search(self, query: str, k: int = 3) -> list[Document]:
        """Perform similarity search in the knowledge base."""
        if self.vector_store is None or not query.strip() or k <= 0:
            return []

        return self.vector_store.similarity_search(query, k=k)

    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> list[tuple]:
        """Perform similarity search with relevance scores."""
        if self.vector_store is None or not query.strip() or k <= 0:
            return []

        return self.vector_store.similarity_search_with_score(query, k=k)

    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query, respecting token limits."""
        docs = self.similarity_search(query, k=5)

        context_parts = []
        current_tokens = 0

        for doc in docs:
            doc_tokens = len(doc.page_content) // 4

            if current_tokens + doc_tokens <= max_tokens:
                context_parts.append(doc.page_content)
                current_tokens += doc_tokens
            else:
                remaining_chars = (max_tokens - current_tokens) * 4
                if remaining_chars > 100:
                    context_parts.append(doc.page_content[:remaining_chars])
                break

        return '\n\n'.join(context_parts)

    def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        self.documents.clear()
        self.vector_store = None

    def get_document_count(self) -> int:
        """Get the number of documents in the knowledge base."""
        return len(self.documents)

    def save_vector_store(self, path: str) -> None:
        """Save the vector store to disk."""
        if self.vector_store is not None:
            self.vector_store.save_local(path)

    def load_vector_store(self, path: str) -> None:
        """Load a vector store from disk."""
        if os.path.exists(path):
            self.vector_store = FAISS.load_local(
                path, self.embeddings, allow_dangerous_deserialization=True
            )
