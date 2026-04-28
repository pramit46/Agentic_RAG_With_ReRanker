"""
Vector Store Module using ChromaDB
Handles document embedding, storage, and semantic similarity search
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from config import config
import uuid

class VectorStore:
    """
    Vector database implementation using ChromaDB
    Provides semantic search capabilities for document retrieval
    """
    
    def __init__(self):
        """
        Initialize ChromaDB client and embedding model
        Creates persistent storage for vector embeddings
        """
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.Client(Settings(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection_name = "rag_documents"
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"✓ Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document collection for RAG"}
            )
            print(f"✓ Created new collection: {self.collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store with embeddings
        
        Args:
            documents: List of document dictionaries with 'text', 'metadata' keys
        """
        if not documents:
            return
        
        # Extract texts and metadata
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True).tolist()
        
        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✓ Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search using vector embeddings
        
        Args:
            query: Search query text
            top_k: Number of results to return (defaults to config.TOP_K_VECTOR)
        
        Returns:
            List of documents with similarity scores and metadata
        """
        if top_k is None:
            top_k = config.TOP_K_VECTOR
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "source": "vector_search",
                    "id": results["ids"][0][i]
                })
        
        return documents
    
    def get_collection_count(self) -> int:
        """
        Get the total number of documents in the collection
        
        Returns:
            Number of documents stored
        """
        return self.collection.count()
    
    def reset(self) -> None:
        """
        Reset the vector store by deleting and recreating the collection
        Use with caution - this removes all stored documents
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Document collection for RAG"}
        )
        print(f"✓ Reset collection: {self.collection_name}")
