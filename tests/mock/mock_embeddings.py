"""Mock embeddings for testing that don't call external APIs."""

from langchain.embeddings.base import Embeddings


class MockEmbeddings(Embeddings):
    """Mock embeddings for testing that don't call external APIs."""

    def _create_semantic_embedding(self, text: str) -> list[float]:
        """Create a simple semantic embedding based on keywords."""
        embedding = [0.0] * 384

        words = text.lower().split()

        for word in words:
            word_hash = hash(word) % 1000
            base_index = (word_hash % 100) * 3

            if base_index < 384:
                embedding[base_index] += 0.5
            if base_index + 1 < 384:
                embedding[base_index + 1] += 0.3
            if base_index + 2 < 384:
                embedding[base_index + 2] += 0.2

        max_val = max(abs(x) for x in embedding) or 1
        return [x / max_val for x in embedding]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return mock embeddings for documents."""
        return [self._create_semantic_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return mock embedding for query."""
        return self._create_semantic_embedding(text)
