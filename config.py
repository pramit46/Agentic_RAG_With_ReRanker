"""
Configuration Module for Agentic RAG Application
Loads environment variables and provides centralized configuration
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration class for the application
    All settings are loaded from environment variables with sensible defaults
    """
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"
    
    # OpenAI Configuration (only needed if using OpenAI)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Ollama Configuration (only needed if using Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Neo4j Graph Database Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # ChromaDB Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Retrieval Configuration
    TOP_K_VECTOR: int = int(os.getenv("TOP_K_VECTOR", "5"))
    TOP_K_BM25: int = int(os.getenv("TOP_K_BM25", "5"))
    TOP_K_GRAPH: int = int(os.getenv("TOP_K_GRAPH", "3"))
    FINAL_TOP_K: int = int(os.getenv("FINAL_TOP_K", "10"))
    
    # HITL Re-ranking Configuration
    HITL_BOOST_FACTOR: float = float(os.getenv("HITL_BOOST_FACTOR", "2.0"))
    HITL_DECAY_FACTOR: float = float(os.getenv("HITL_DECAY_FACTOR", "0.95"))
    
    # Persistence paths
    HITL_FEEDBACK_FILE: str = "./hitl_feedback.json"
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configurations are set
        Returns True if configuration is valid, raises ValueError otherwise
        """
        # Validate based on LLM provider
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai. Please set it in .env file")
        
        if cls.LLM_PROVIDER == "ollama":
            print(f"✓ Using Ollama at {cls.OLLAMA_BASE_URL} with model {cls.OLLAMA_MODEL}")
        
        if cls.LLM_PROVIDER not in ["openai", "ollama"]:
            raise ValueError(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'openai' or 'ollama'")
        
        # Create necessary directories
        Path(cls.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
        
        return True

# Create a global config instance
config = Config()
