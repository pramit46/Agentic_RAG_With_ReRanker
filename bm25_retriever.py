"""
BM25 Retriever Module
Implements BM25 (Best Matching 25) algorithm for keyword-based retrieval
"""
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Optional
import string
from config import config

class BM25Retriever:
    """
    BM25-based retrieval system for keyword matching
    Complements semantic search with traditional IR methods
    """
    
    def __init__(self):
        """
        Initialize the BM25 retriever
        Corpus will be built when documents are added
        """
        self.corpus = []  # List of tokenized documents
        self.documents = []  # Original documents with metadata
        self.bm25 = None
        print("✓ Initialized BM25 retriever")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25 indexing
        Converts to lowercase and removes punctuation
        
        Args:
            text: Input text to tokenize
        
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Split into tokens
        tokens = text.split()
        
        return tokens
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the BM25 index
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata' keys
        """
        if not documents:
            return
        
        # Store original documents
        self.documents.extend(documents)
        
        # Tokenize and add to corpus
        for doc in documents:
            tokens = self._tokenize(doc["text"])
            self.corpus.append(tokens)
        
        # Build or rebuild BM25 index
        self.bm25 = BM25Okapi(self.corpus)
        
        print(f"✓ Added {len(documents)} documents to BM25 index (Total: {len(self.documents)})")
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search documents using BM25 algorithm
        
        Args:
            query: Search query text
            top_k: Number of results to return (defaults to config.TOP_K_BM25)
        
        Returns:
            List of documents with BM25 scores
        """
        if top_k is None:
            top_k = config.TOP_K_BM25
        
        if not self.bm25 or not self.documents:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include documents with positive scores
                doc = self.documents[idx].copy()
                doc["score"] = float(scores[idx])
                doc["source"] = "bm25_search"
                if "id" not in doc:
                    doc["id"] = f"bm25_{idx}"
                results.append(doc)
        
        return results
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the index
        
        Returns:
            Number of documents indexed
        """
        return len(self.documents)
    
    def reset(self) -> None:
        """
        Reset the BM25 index by clearing all documents
        Use with caution - this removes all indexed documents
        """
        self.corpus = []
        self.documents = []
        self.bm25 = None
        print("✓ Reset BM25 index")
