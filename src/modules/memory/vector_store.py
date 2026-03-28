import os
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import List, Optional
from src.core.settings import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
import uuid

from langchain_openai import OpenAIEmbeddings


@dataclass
class Memory:
    """Represents a memory entry in the vector store."""

    text: str
    metadata: dict
    score: Optional[float] = None

    @property
    def id(self) -> Optional[str]:
        return self.metadata.get("id")

    @property
    def timestamp(self) -> Optional[datetime]:
        ts = self.metadata.get("timestamp")
        return datetime.fromisoformat(ts) if ts else None
    


class VectorStore:
    def __init__(self, collection_name: str="The-Memories"):
        # self.collection_name = collection_name
        self.client = self._get_qdrant_client()

        self.model = OpenAIEmbeddings(model="text-embedding-3-large",api_key=settings.OPENAI_API_KEY)  # Use the same model for embeddings
        self.SIMILARITY_THRESHOLD = 0.6
        self.COLLECTION_NAME = collection_name

    @lru_cache(maxsize=1)
    def _get_qdrant_client(self) -> QdrantClient:
       

        return QdrantClient(
            url=settings.QDRANT_URL,   # full URL
            api_key=settings.QDRANT_API_KEY,  # MUST NOT be None
            timeout=30  # optional but useful
        )
    def _collection_exists(self) -> bool:
        """Check if the memory collection exists."""
        collections = self.client.get_collections().collections
        return any(col.name == self.COLLECTION_NAME for col in collections)

    def _create_collection(self) -> None:
        """Create a new collection for storing memories."""
        sample_embedding = self.model.embed_query("Sample memory text")
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=len(sample_embedding),
                distance=Distance.COSINE,
            ),
        )

    def find_similar_memory(self, text: str) -> Optional[Memory]:
        """Find if a similar memory already exists.

        Args:
            text: The text to search for

        Returns:
            Optional Memory if a similar one is found
        """
        results = self.search_memories(text, k=1)
        print(f"Similarity search results: {results[0].score if results else 'No results'}")
        if results and results[0].score >= self.SIMILARITY_THRESHOLD:
            return results[0]
        #store if very disimilar
        return None

    def store_memory(self, text: str, metadata: dict) -> None:
        """Store a new memory in the vector store or update if similar exists.

        Args:
            text: The text content of the memory
            metadata: Additional information about the memory (timestamp, type, etc.)
        """
        if not self._collection_exists():
            self._create_collection()

        # Check if similar memory exists
        similar_memory = self.find_similar_memory(text)
        if similar_memory and similar_memory.id:
            metadata["id"] = similar_memory.id  # Keep same ID for update

    # id = metadata.get("id", str(uuid.uuid4()))
        embedding = self.model.embed_query(text)
        point = PointStruct(
            id=metadata.get("id", str(uuid.uuid4())),  # Use existing ID or generate new one
            vector=embedding,
            payload={
                "text": text,
                **metadata,
            },
        )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )

    def search_memories(self, query: str, k: int = 5) -> List[Memory]:
        if not self._collection_exists():
            return []

        query_embedding = self.model.embed_query(query)

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            limit=k,
        )

        return [
            Memory(
                text=hit.payload["text"],
                metadata={k: v for k, v in hit.payload.items() if k != "text"},
                score=hit.score,
            )
            for hit in results.points
        ]
    
# if __name__ == "__main__":
#     store = VectorStore()
#     store.store_memory("I had a great day at the park!", {"timestamp": datetime.now().isoformat(), "type": "experience"})
#     similar = store.find_similar_memory("My nice day at the park")
#     print(similar)
#     similar = store.find_similar_memory("I had a good day at the park")
#     print(similar)

#python -m src.modules.memory.vector_store

@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Get a singleton instance of the VectorStore."""
    return VectorStore()