from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Initialize ChromaDB client and collection if available
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            self._use_chroma = True
        except Exception:
            # Fall back to in-memory store if ChromaDB not available
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Create a normalized record for storing one document.
        
        Returns:
            {
                "id": int,  # Internal auto-incrementing ID
                "doc_id": str,  # Original document ID
                "content": str,  # Document content
                "embedding": list[float],  # Embedded vector
                "metadata": dict,  # Document metadata
            }
        """
        # Embed the document content
        embedding = self._embedding_fn(doc.content)
        
        # Create record with auto-incremented ID
        record = {
            "id": self._next_index,
            "doc_id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": doc.metadata,
        }
        
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Search in-memory by computing similarity to all records.
        
        Args:
            query: Query text to embed and search for
            records: List of stored records to search within
            top_k: Number of top results to return
        
        Returns:
            List of top_k records sorted by descending similarity
        """
        if not records:
            return []
        
        # Embed the query
        query_embedding = self._embedding_fn(query)
        
        # Compute similarity for each record
        scored_records = []
        for record in records:
            similarity = _dot(query_embedding, record["embedding"])
            scored_records.append((similarity, record))
        
        # Sort by similarity (descending) and return top_k
        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [{**record, "score": score} for score, record in scored_records[:top_k]]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return
        
        if self._use_chroma and self._collection:
            # ChromaDB path: batch add
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            
            for doc in docs:
                record = self._make_record(doc)
                ids.append(str(record["id"]))
                documents.append(record["content"])
                embeddings.append(record["embedding"])
                metadatas.append({"doc_id": record["doc_id"], **record["metadata"]})
            
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        else:
            # In-memory path: append records to store
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection:
            # ChromaDB path
            results = self._collection.query(query_texts=[query], n_results=top_k)
            # ChromaDB returns structure: {"ids": [...], "documents": [...], "embeddings": [...], "metadatas": [...], "distances": [...]}
            # Convert to our record format with score
            output = []
            for i in range(len(results["documents"][0])):
                # ChromaDB distances are already in descending order of relevance
                score = 1.0 - results["distances"][0][i] if results.get("distances") else 0.0
                output.append({
                    "id": int(results["ids"][0][i]),
                    "content": results["documents"][0][i],
                    "embedding": results["embeddings"][0][i] if results["embeddings"] else [],
                    "metadata": results["metadatas"][0][i],
                    "score": score,
                })
            return output
        else:
            # In-memory path: use helper method
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        
        Args:
            query: Query text
            top_k: Number of results to return
            metadata_filter: Dict of {key: value} to match in metadata
        
        Example:
            search_with_filter("hello", top_k=3, metadata_filter={"lang": "en", "source": "FAQ"})
        """
        if metadata_filter is None:
            metadata_filter = {}
        
        if self._use_chroma and self._collection:
            # ChromaDB path: use where clause for filtering
            # Build ChromaDB where clause (simplified for exact matches)
            where_clause = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append({key: {"$eq": value}})
                if len(conditions) == 1:
                    where_clause = conditions[0]
                elif len(conditions) > 1:
                    where_clause = {"$and": conditions}
            
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause
            )
            output = []
            for i in range(len(results["documents"][0])):
                score = 1.0 - results["distances"][0][i] if results.get("distances") else 0.0
                output.append({
                    "id": int(results["ids"][0][i]),
                    "content": results["documents"][0][i],
                    "embedding": results["embeddings"][0][i] if results["embeddings"] else [],
                    "metadata": results["metadatas"][0][i],
                    "score": score,
                })
            return output
        else:
            # In-memory path: filter first, then search
            filtered_records = []
            for record in self._store:
                # Check if record matches all filter criteria
                match = True
                for key, value in metadata_filter.items():
                    if record["metadata"].get(key) != value:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
            
            # Search among filtered records
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection:
            # ChromaDB path: delete by where clause
            # Get IDs first
            try:
                results = self._collection.get(where={"doc_id": {"$eq": doc_id}})
                if results and results["ids"]:
                    self._collection.delete(ids=results["ids"])
                    return len(results["ids"]) > 0
                return False
            except Exception:
                return False
        else:
            # In-memory path: filter out records with matching doc_id
            before_count = len(self._store)
            self._store = [r for r in self._store if r["doc_id"] != doc_id]
            after_count = len(self._store)
            return after_count < before_count
