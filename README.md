# 🤖 Agentic RAG with HITL Re-ranking

A production-ready Retrieval-Augmented Generation (RAG) system that combines:
- **Vector Database** (ChromaDB) for semantic search
- **Graph Database** (Neo4j) for relationship-based retrieval
- **BM25** for traditional keyword matching
- **Human-in-the-Loop (HITL)** re-ranking with implicit feedback learning

## ✨ Features

### Multi-Source Retrieval
- **Vector Search**: Semantic similarity using sentence transformers
- **BM25 Search**: Probabilistic keyword-based retrieval
- **Graph Search**: Relationship and entity-based queries via Neo4j
- **Fusion Ranking**: Reciprocal Rank Fusion (RRF) to combine results

### Intelligent Re-ranking
- **HITL Learning**: Learns from user selections via implicit feedback
- **Automatic Boosting**: Selected documents rank higher in future similar queries
- **Decay Mechanism**: Older feedback gradually decays to prioritize recent patterns
- **Cross-Query Learning**: Applies learnings to similar queries automatically

### Production Features
- Persistent storage for all data (vectors, graphs, feedback)
- Comprehensive error handling and logging
- Rich CLI interface with beautiful formatting
- Configurable via environment variables
- Modular, extensible architecture

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Neo4j Database** (should be running at `localhost:7474`)
3. **OpenAI API Key** (for LLM and embeddings)

### Installation

1. **Clone or navigate to the project directory**

```bash
cd Agentic_RAG_With_ReRanker
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment**

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Ensure Neo4j is running**

```bash
# Neo4j should be accessible at:
# URI: bolt://localhost:7687
# User: neo4j
# Password: password
```

5. **Run the application**

```bash
python main.py
```

## 📖 Usage

### Interactive Mode

The application starts in interactive mode with a CLI interface:

```
Query: What is RAG and how does it work?
```

The system will:
1. Retrieve relevant documents from all sources
2. Apply fusion ranking and HITL re-ranking
3. Generate a comprehensive answer using LLM
4. Ask if you want to provide feedback

### Commands

- **Enter any question** - Query the system
- `sample` - Show example queries
- `stats` - Display system statistics
- `reset` - Reset HITL feedback data
- `help` - Show help message
- `exit` - Exit the application

### HITL Feedback

After each query, you can select which document was most helpful. This selection:
- Boosts that document's ranking for similar future queries
- Learns patterns across related queries
- Improves system performance over time

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Agentic RAG Orchestrator                   │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Vector    │  │    BM25     │  │   Graph     │
│   Search    │  │   Search    │  │   Search    │
│  (ChromaDB) │  │  (rank-bm25)│  │   (Neo4j)   │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │  Fusion Ranking     │
              │  (RRF Algorithm)    │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  HITL Re-ranking    │
              │  (Implicit Feedback)│
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   LLM Generation    │
              │    (OpenAI GPT)     │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Final Answer      │
              └─────────────────────┘
```

## 📁 Project Structure

```
.
├── agent.py              # Agentic RAG orchestrator
├── vector_store.py       # ChromaDB vector database
├── graph_store.py        # Neo4j graph database
├── bm25_retriever.py     # BM25 keyword search
├── hitl_reranker.py      # HITL re-ranking with implicit feedback
├── config.py             # Configuration management
├── sample_data.py        # Sample documents and queries
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🔧 Configuration

Edit `.env` to customize the system:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Retrieval Settings
TOP_K_VECTOR=5          # Top results from vector search
TOP_K_BM25=5            # Top results from BM25
TOP_K_GRAPH=3           # Top results from graph search
FINAL_TOP_K=10          # Final number of results to return

# HITL Configuration
HITL_BOOST_FACTOR=2.0   # How much to boost selected documents
HITL_DECAY_FACTOR=0.95  # Decay rate for old feedback
```

## 📊 How HITL Re-ranking Works

### Implicit Feedback Learning

1. **User Selection**: When a user indicates a document was helpful
2. **Feedback Recording**: System records (query, document) pair
3. **Cross-Query Application**: For future similar queries, that document gets boosted
4. **Similarity Matching**: Uses word overlap to find similar queries
5. **Score Boosting**: Original score × (1 + boost_factor × similarity × selection_count)
6. **Temporal Decay**: Older selections gradually decay in influence

### Example

```
Query 1: "What is RAG?"
User selects: Document about RAG fundamentals

Query 2: "How does RAG work?" (similar to Query 1)
→ RAG fundamentals document gets boosted automatically!
```

## 🎯 Key Components

### Vector Store (ChromaDB)
- Stores document embeddings using Sentence-BERT
- Performs semantic similarity search
- Persistent storage for embeddings

### Graph Store (Neo4j)
- Stores documents as nodes with entity relationships
- Enables graph traversal queries
- Captures semantic relationships between concepts

### BM25 Retriever
- Traditional probabilistic retrieval
- Excellent for exact keyword matching
- Complements semantic search

### HITL Re-ranker
- Records user selections as implicit feedback
- Boosts relevant documents for similar queries
- Self-improving system over time

## 🔒 Security Notes

- Never commit `.env` file with real API keys
- Use environment variables for sensitive configuration
- Neo4j credentials should be changed from defaults in production

## 🐛 Troubleshooting

### "Failed to connect to Neo4j"
- Ensure Neo4j is running: Check `localhost:7474`
- Verify credentials in `.env` match your Neo4j setup

### "OPENAI_API_KEY is required"
- Add your OpenAI API key to `.env` file
- Ensure the `.env` file is in the project root

### ChromaDB issues
- Delete `./chroma_db` directory to reset
- Ensure sufficient disk space for embeddings

## 📝 License

This project is provided as-is for educational and production use.

## 🤝 Contributing

Contributions welcome! The modular architecture makes it easy to:
- Add new retrieval methods
- Implement different re-ranking algorithms
- Integrate additional data sources
- Enhance HITL feedback mechanisms

## 📚 References

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Neo4j Graph Database](https://neo4j.com/)
- [LangChain Framework](https://python.langchain.com/)

---

Built with ❤️ for production AI applications
