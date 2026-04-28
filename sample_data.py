"""
Sample Data Module
Provides sample documents for testing the Agentic RAG system
"""
from typing import List, Dict, Any

def get_sample_documents() -> List[Dict[str, Any]]:
    """
    Generate sample documents for demonstration
    These cover various topics in AI, machine learning, and technology
    
    Returns:
        List of document dictionaries with text, metadata, and entities
    """
    documents = [
        {
            "id": "doc_1",
            "text": "Retrieval-Augmented Generation (RAG) is a powerful technique that combines the strengths of large language models with external knowledge retrieval. By fetching relevant documents from a knowledge base, RAG systems can provide more accurate and contextually relevant responses.",
            "metadata": {
                "category": "AI",
                "topic": "RAG",
                "date": "2024-01-15"
            },
            "entities": [
                {"name": "RAG", "type": "Technique", "relationship": "MENTIONS"},
                {"name": "LLM", "type": "Technology", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_2",
            "text": "Vector databases like ChromaDB, Pinecone, and Weaviate enable efficient semantic search by storing document embeddings. These embeddings capture the semantic meaning of text, allowing for similarity-based retrieval that goes beyond simple keyword matching.",
            "metadata": {
                "category": "Databases",
                "topic": "Vector Search",
                "date": "2024-01-20"
            },
            "entities": [
                {"name": "ChromaDB", "type": "Database", "relationship": "MENTIONS"},
                {"name": "Pinecone", "type": "Database", "relationship": "MENTIONS"},
                {"name": "Weaviate", "type": "Database", "relationship": "MENTIONS"},
                {"name": "Vector Search", "type": "Technique", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_3",
            "text": "Graph databases like Neo4j excel at storing and querying connected data. They use nodes, relationships, and properties to represent complex interconnections, making them ideal for knowledge graphs, recommendation systems, and social networks.",
            "metadata": {
                "category": "Databases",
                "topic": "Graph Databases",
                "date": "2024-01-25"
            },
            "entities": [
                {"name": "Neo4j", "type": "Database", "relationship": "MENTIONS"},
                {"name": "Knowledge Graph", "type": "Concept", "relationship": "RELATES_TO"},
                {"name": "Graph Database", "type": "Technology", "relationship": "MENTIONS"}
            ]
        },
        {
            "id": "doc_4",
            "text": "BM25 (Best Matching 25) is a ranking function used in information retrieval. It's based on the probabilistic retrieval framework and considers term frequency, inverse document frequency, and document length normalization. Despite being a traditional method, it remains highly effective for keyword-based search.",
            "metadata": {
                "category": "Information Retrieval",
                "topic": "BM25",
                "date": "2024-02-01"
            },
            "entities": [
                {"name": "BM25", "type": "Algorithm", "relationship": "MENTIONS"},
                {"name": "Information Retrieval", "type": "Field", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_5",
            "text": "Human-in-the-Loop (HITL) systems incorporate human feedback to improve machine learning models. In re-ranking scenarios, implicit feedback from user selections can be used to boost relevant results in future queries, creating a self-improving system.",
            "metadata": {
                "category": "Machine Learning",
                "topic": "HITL",
                "date": "2024-02-05"
            },
            "entities": [
                {"name": "HITL", "type": "Technique", "relationship": "MENTIONS"},
                {"name": "Machine Learning", "type": "Field", "relationship": "RELATES_TO"},
                {"name": "Re-ranking", "type": "Technique", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_6",
            "text": "Embedding models like Sentence-BERT and OpenAI's text-embedding-ada-002 convert text into dense vector representations. These embeddings capture semantic relationships, enabling neural search capabilities that understand context and meaning rather than just matching keywords.",
            "metadata": {
                "category": "NLP",
                "topic": "Embeddings",
                "date": "2024-02-10"
            },
            "entities": [
                {"name": "Sentence-BERT", "type": "Model", "relationship": "MENTIONS"},
                {"name": "OpenAI", "type": "Organization", "relationship": "MENTIONS"},
                {"name": "Embeddings", "type": "Technique", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_7",
            "text": "Hybrid search combines multiple retrieval methods to leverage their complementary strengths. By fusing results from vector search, keyword search (BM25), and graph traversal, hybrid systems achieve better recall and precision than any single method alone.",
            "metadata": {
                "category": "Search",
                "topic": "Hybrid Search",
                "date": "2024-02-15"
            },
            "entities": [
                {"name": "Hybrid Search", "type": "Technique", "relationship": "MENTIONS"},
                {"name": "Vector Search", "type": "Technique", "relationship": "RELATES_TO"},
                {"name": "BM25", "type": "Algorithm", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_8",
            "text": "LangChain is a framework for developing applications powered by language models. It provides tools for prompt management, chains, agents, and memory, making it easier to build sophisticated LLM applications with external data sources and APIs.",
            "metadata": {
                "category": "Frameworks",
                "topic": "LangChain",
                "date": "2024-02-20"
            },
            "entities": [
                {"name": "LangChain", "type": "Framework", "relationship": "MENTIONS"},
                {"name": "LLM", "type": "Technology", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_9",
            "text": "Reciprocal Rank Fusion (RRF) is an effective method for combining rankings from multiple sources. It assigns scores based on the reciprocal of the rank position, making it more robust to outliers than score-based fusion methods.",
            "metadata": {
                "category": "Information Retrieval",
                "topic": "Rank Fusion",
                "date": "2024-02-25"
            },
            "entities": [
                {"name": "RRF", "type": "Algorithm", "relationship": "MENTIONS"},
                {"name": "Rank Fusion", "type": "Technique", "relationship": "RELATES_TO"}
            ]
        },
        {
            "id": "doc_10",
            "text": "Agentic systems use AI agents that can reason, plan, and take actions to accomplish complex tasks. These agents can break down problems, use tools, retrieve information, and adapt their strategies based on intermediate results and feedback.",
            "metadata": {
                "category": "AI",
                "topic": "AI Agents",
                "date": "2024-03-01"
            },
            "entities": [
                {"name": "AI Agents", "type": "Concept", "relationship": "MENTIONS"},
                {"name": "Agentic Systems", "type": "Concept", "relationship": "RELATES_TO"}
            ]
        }
    ]
    
    return documents

def get_sample_queries() -> List[str]:
    """
    Generate sample queries for testing the system
    
    Returns:
        List of query strings
    """
    return [
        "What is RAG and how does it work?",
        "How do vector databases enable semantic search?",
        "What are the advantages of using Neo4j?",
        "Explain BM25 algorithm",
        "How does human-in-the-loop improve systems?",
        "What is hybrid search?",
        "Tell me about embedding models",
        "How can I combine multiple search methods?"
    ]
