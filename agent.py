"""
Agentic RAG Orchestrator
Coordinates retrieval from multiple sources and synthesizes final answers
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from vector_store import VectorStore
from graph_store import GraphStore
from bm25_retriever import BM25Retriever
from hitl_reranker import HITLReranker
from config import config
import time

class AgenticRAG:
    """
    Agentic RAG system that intelligently orchestrates multiple retrieval methods
    Combines vector search, graph traversal, BM25, and HITL re-ranking
    """
    
    def __init__(self):
        """
        Initialize all components of the agentic RAG system
        """
        print("\n🚀 Initializing Agentic RAG System...")
        
        # Initialize LLM
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in .env file")
        
        self.llm = ChatOpenAI(
            model=config.LLM_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Initialize retrieval components
        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.bm25_retriever = BM25Retriever()
        self.hitl_reranker = HITLReranker()
        
        print("✅ Agentic RAG System initialized successfully\n")
    
    def _deduplicate_results(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate documents based on text content
        Keeps the version with the highest score
        
        Args:
            documents: List of documents from various sources
        
        Returns:
            Deduplicated list of documents
        """
        seen_texts = {}
        
        for doc in documents:
            text = doc.get("text", "")
            
            if text not in seen_texts:
                seen_texts[text] = doc
            else:
                # Keep the one with higher score
                if doc.get("score", 0) > seen_texts[text].get("score", 0):
                    seen_texts[text] = doc
        
        return list(seen_texts.values())
    
    def _fusion_ranking(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply fusion ranking to combine scores from multiple retrieval methods
        Uses Reciprocal Rank Fusion (RRF) algorithm
        
        Args:
            documents: List of documents with scores from different sources
        
        Returns:
            Documents with fused scores
        """
        # Group by source
        source_rankings = {}
        for doc in documents:
            source = doc.get("source", "unknown")
            if source not in source_rankings:
                source_rankings[source] = []
            source_rankings[source].append(doc)
        
        # Sort each source's results by score
        for source in source_rankings:
            source_rankings[source] = sorted(
                source_rankings[source],
                key=lambda x: x.get("score", 0),
                reverse=True
            )
        
        # Calculate RRF scores
        k = 60  # RRF constant
        rrf_scores = {}
        
        for doc in documents:
            doc_text = doc.get("text", "")
            if doc_text not in rrf_scores:
                rrf_scores[doc_text] = {"score": 0, "doc": doc}
            
            # Find rank in source
            source = doc.get("source", "unknown")
            if source in source_rankings:
                try:
                    rank = source_rankings[source].index(doc) + 1
                    rrf_scores[doc_text]["score"] += 1 / (k + rank)
                except ValueError:
                    pass
        
        # Create final ranked list
        fused_docs = []
        for text, data in rrf_scores.items():
            doc = data["doc"].copy()
            doc["original_score"] = doc.get("score", 0)
            doc["fusion_score"] = data["score"]
            doc["score"] = data["score"]
            fused_docs.append(doc)
        
        return sorted(fused_docs, key=lambda x: x.get("score", 0), reverse=True)
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform multi-source retrieval using vector search, BM25, and graph traversal
        
        Args:
            query: User's search query
        
        Returns:
            Combined and ranked list of relevant documents
        """
        print(f"\n🔍 Retrieving documents for query: '{query}'")
        
        all_documents = []
        
        # 1. Vector search (semantic similarity)
        print("  ↳ Performing vector search...")
        vector_results = self.vector_store.similarity_search(query)
        all_documents.extend(vector_results)
        print(f"    Found {len(vector_results)} results")
        
        # 2. BM25 search (keyword matching)
        print("  ↳ Performing BM25 search...")
        bm25_results = self.bm25_retriever.search(query)
        all_documents.extend(bm25_results)
        print(f"    Found {len(bm25_results)} results")
        
        # 3. Graph search (relationship-based)
        print("  ↳ Performing graph search...")
        graph_results = self.graph_store.graph_search(query)
        all_documents.extend(graph_results)
        print(f"    Found {len(graph_results)} results")
        
        # Deduplicate results
        unique_documents = self._deduplicate_results(all_documents)
        print(f"  ↳ After deduplication: {len(unique_documents)} unique documents")
        
        # Apply fusion ranking
        fused_documents = self._fusion_ranking(unique_documents)
        
        # Apply HITL re-ranking
        print("  ↳ Applying HITL re-ranking...")
        reranked_documents = self.hitl_reranker.rerank(query, fused_documents)
        
        # Get top-k results
        top_documents = reranked_documents[:config.FINAL_TOP_K]
        
        print(f"✓ Retrieved {len(top_documents)} final documents\n")
        
        return top_documents
    
    def _create_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Create context string from retrieved documents
        
        Args:
            documents: List of retrieved documents
        
        Returns:
            Formatted context string for LLM
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.get("source", "unknown")
            score = doc.get("score", 0)
            text = doc.get("text", "")
            boosted = doc.get("boosted", False)
            
            boost_marker = " [★HITL BOOSTED]" if boosted else ""
            
            context_parts.append(
                f"Document {i} (Source: {source}, Score: {score:.3f}{boost_marker}):\n{text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def generate_answer(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate final answer using LLM with retrieved context
        
        Args:
            query: User's query
            documents: Retrieved and ranked documents
        
        Returns:
            Dictionary containing answer and metadata
        """
        print("🤖 Generating answer with LLM...")
        
        # Create context from documents
        context = self._create_context(documents)
        
        # Create prompt
        system_prompt = """You are an expert AI assistant with access to a knowledge base. 
Your task is to provide accurate, comprehensive answers based on the provided context.

Guidelines:
1. Answer the question using ONLY information from the provided context
2. If the context doesn't contain enough information, say so honestly
3. Cite document numbers when referencing specific information
4. Be concise but thorough
5. If documents are marked as [★HITL BOOSTED], they have been selected by users as particularly relevant"""
        
        user_prompt = f"""Context from knowledge base:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""
        
        # Generate response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        start_time = time.time()
        response = self.llm.invoke(messages)
        generation_time = time.time() - start_time
        
        answer = response.content
        
        print(f"✓ Generated answer in {generation_time:.2f}s\n")
        
        return {
            "answer": answer,
            "documents": documents,
            "generation_time": generation_time,
            "query": query
        }
    
    def query(self, query: str) -> Dict[str, Any]:
        """
        Main query method - performs full RAG pipeline
        
        Args:
            query: User's query
        
        Returns:
            Complete response with answer and supporting documents
        """
        # Retrieve relevant documents
        documents = self.retrieve(query)
        
        # Generate answer
        result = self.generate_answer(query, documents)
        
        return result
    
    def record_user_selection(self, query: str, document_index: int, documents: List[Dict[str, Any]]) -> None:
        """
        Record when user selects a specific document
        This provides implicit feedback for HITL learning
        
        Args:
            query: The original query
            document_index: Index of the selected document (0-based)
            documents: The list of documents that were presented
        """
        if 0 <= document_index < len(documents):
            selected_doc = documents[document_index]
            self.hitl_reranker.record_selection(query, selected_doc)
            print(f"✓ Recorded user selection: Document #{document_index + 1}")
        else:
            print(f"⚠ Invalid document index: {document_index}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to all retrieval systems
        
        Args:
            documents: List of documents to add
        """
        print(f"\n📚 Adding {len(documents)} documents to all stores...")
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        # Add to BM25
        self.bm25_retriever.add_documents(documents)
        
        # Add to graph store (if entities are provided)
        self.graph_store.add_documents_with_entities(documents)
        
        print("✅ Documents added to all stores\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system
        
        Returns:
            Dictionary with system statistics
        """
        return {
            "vector_store_count": self.vector_store.get_collection_count(),
            "bm25_index_count": self.bm25_retriever.get_document_count(),
            "hitl_stats": self.hitl_reranker.get_statistics()
        }
    
    def close(self):
        """
        Close all connections and cleanup resources
        """
        self.graph_store.close()
        print("✓ Closed all connections")
