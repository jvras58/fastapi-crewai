"""Controller for chat and conversation management."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from apps.core.models.user import User
from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.api.documents.schemas import DocumentUploadSchema
from apps.ia.models.document import Document
from apps.ia.services.rag_service import RAGService
from apps.packpage.generic_controller import GenericController


class DocController(GenericController):
    """Controller for chat operations."""

    def __init__(
        self, rag_service: RAGService = None, init_agent: bool = True
    ) -> None:
        """Initialize document controller."""
        super().__init__(Document)
        self.rag_service = rag_service or RAGService()
        self.conversation_agent = None
        if init_agent:
            try:
                self.conversation_agent = ConversationAgent(self.rag_service)
            except ValueError:
                self.conversation_agent = None

    def upload_document(
        self,
        session: Session,
        document_data: DocumentUploadSchema,
        current_user: User,
        request_ip: str,
    ) -> Document:
        """Upload document to knowledge base."""

        content_hash = hashlib.sha256(
            document_data.txt_content.encode('utf-8')
        ).hexdigest()

        existing_doc = (
            session.query(Document)
            .filter(Document.str_content_hash == content_hash)
            .first()
        )

        if existing_doc:
            raise ValueError('Documento com este conteúdo já existe')

        document = Document(
            str_title=document_data.str_title,
            str_filename=document_data.str_filename,
            txt_content=document_data.txt_content,
            str_content_type=document_data.str_content_type,
            json_metadata=(
                json.dumps(document_data.json_metadata)
                if document_data.json_metadata
                else None
            ),
            int_size_bytes=len(document_data.txt_content.encode('utf-8')),
            str_content_hash=content_hash,
            str_status='active',
            audit_user_ip=request_ip,
            audit_user_login=current_user.username,
        )

        session.add(document)
        session.commit()

        metadata = document_data.json_metadata or {}
        metadata.update(
            {
                'doc_id': document.id,
                'title': document.str_title,
                'source': f'document_{document.id}',
            }
        )

        self.rag_service.add_document_from_text(
            document_data.txt_content, metadata
        )

        document.dt_processed_at = datetime.now(UTC)
        session.commit()

        return document

    def get_documents(
        self, session: Session, page: int = 1, per_page: int = 20, **filters
    ) -> dict[str, Any]:
        """Get documents with pagination using GenericController."""
        skip = (page - 1) * per_page

        if 'str_status' not in filters:
            filters['str_status'] = 'active'

        documents = self.get_all(session, skip=skip, limit=per_page, **filters)

        total_query = session.query(Document)
        if filters:
            for key, value in filters.items():
                if hasattr(Document, key):
                    field = getattr(Document, key)
                    total_query = total_query.filter(field == value)

        total = total_query.count()

        return {
            'documents': documents,
            'total': total,
            'page': page,
            'per_page': per_page,
        }

    def search_knowledge_base(
        self, query: str, k: int = 5
    ) -> list[dict[str, Any]]:
        """Search the knowledge base."""
        docs = self.rag_service.similarity_search(query, k=k)

        results = []
        for doc in docs:
            results.append(
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source', 'unknown'),
                }
            )

        return results

    def get_document_by_id(
        self, session: Session, document_id: int
    ) -> Document:
        """Get a document by ID using GenericController."""
        return self.get(session, document_id)

    def delete_document(self, session: Session, document_id: int) -> None:
        """Delete a document and remove from RAG index."""
        document = self.get(session, document_id)

        if document.dt_processed_at:
            try:
                document.str_status = 'deleted'
                session.commit()
            except Exception:
                pass

        self.delete(session, document_id)

    def update_document_status(
        self, session: Session, document_id: int, status: str
    ) -> Document:
        """Update document status."""
        document = self.get(session, document_id)
        document.str_status = status

        if status == 'processed':
            document.dt_processed_at = datetime.now(UTC)

        return self.update(session, document)

    def search_documents_by_content(
        self, session: Session, search_term: str, limit: int = 10
    ) -> list[Document]:
        """Search documents by content using database search."""
        return self.get_all(
            session,
            limit=limit,
            txt_content=search_term,
            str_status='active',
        )

    def get_documents_by_type(
        self, session: Session, content_type: str, limit: int = 20
    ) -> list[Document]:
        """Get documents filtered by content type using GenericController."""
        return self.get_all(
            session,
            limit=limit,
            str_content_type=content_type,
            str_status='active',
        )

    def get_recent_documents(
        self, session: Session, days: int = 7, limit: int = 10
    ) -> list[Document]:
        """Get recent documents - combining GenericController with custom queries."""
        from datetime import timedelta

        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        base_query = (
            session.query(Document)
            .filter(
                Document.str_status == 'active',
                Document.dt_uploaded_at >= cutoff_date,
            )
            .order_by(Document.dt_uploaded_at.desc())
            .limit(limit)
        )

        return list(base_query.all())
