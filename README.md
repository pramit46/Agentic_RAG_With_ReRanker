# 🤖 Agentic RAG with HITL Re-ranking

A production-ready Retrieval-Augmented Generation (RAG) system that combines:
- **Vector Database** (ChromaDB) for semantic search
- **Graph Database** (Neo4j) for relationship-based retrieval with natural language query support
- **BM25** for traditional keyword matching
- **Human-in-the-Loop (HITL)** re-ranking with implicit feedback learning
- **Flexible LLM Support** - Works with both Ollama (local, free) and OpenAI

## ✨ Features

### Multi-Source Retrieval
- **Vector Search**: Semantic similarity using sentence transformers (`all-MiniLM-L6-v2`)
- **BM25 Search**: Probabilistic keyword-based retrieval with tokenization
- **Graph Search**: Relationship and entity-based queries via Neo4j with intelligent keyword extraction
- **Fusion Ranking**: Reciprocal Rank Fusion (RRF) to combine results optimally

### Intelligent Re-ranking
- **HITL Learning**: Learns from user selections via implicit feedback
- **Automatic Boosting**: Selected documents rank higher in future similar queries
- **Decay Mechanism**: Older feedback gradually decays to prioritize recent patterns
- **Cross-Query Learning**: Applies learnings to similar queries automatically
- **Persistent Memory**: Feedback stored in JSON and survives application restarts

### Advanced Features
- **Natural Language Graph Queries**: Handles questions like "What is Neo4j?" by extracting keywords
- **Case-Insensitive Search**: All search methods handle different cases seamlessly
- **Dual LLM Support**: Switch between Ollama (free, local) and OpenAI (cloud) via config
- **Docker Deployment**: Complete containerized setup with docker-compose

### Production Features
- Persistent storage for all data (vectors, graphs, feedback)
- Comprehensive error handling and logging
- Rich CLI interface with beautiful formatting
- Configurable via environment variables
- Modular, extensible architecture
- Health checks and service dependencies in Docker

### CI/CD & Deployment
- **Jenkins Pipeline**: Automated builds with [Jenkinsfile](Jenkinsfile) → [Setup Guide](JENKINS_ECR_SETUP.md)
- **GitLab CI/CD**: Native GitLab integration with [.gitlab-ci.yml](.gitlab-ci.yml) → [Setup Guide](GITLAB_CI_SETUP.md)
- **AWS ECR**: Both pipelines push to AWS Elastic Container Registry
- **Comparison**: [CI/CD Options Comparison](CI_CD_COMPARISON.md)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

The easiest way to run everything:

```bash
# Start all services (Neo4j + Ollama + App)
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
docker attach rag-application

# Stop everything
docker-compose down
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for complete Docker documentation.

### Option 2: Local Setup

#### Prerequisites

1. **Python 3.12+**
2. **Neo4j Database** (running at `localhost:7474`)
3. **Ollama** (default, free) OR **OpenAI API Key**

#### Installing Ollama (Recommended)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama and pull model
ollama serve
ollama pull llama3.1:8b
```


#### Installation Steps

1. **Clone or navigate to the project directory**

```bash
cd Agentic_RAG_With_ReRanker
```

2. **Create virtual environment**

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**For Ollama (default, free):**
```bash
# .env file
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

**For OpenAI (requires API key):**
```bash
# .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

5. **Ensure Neo4j is running**

```bash
# Neo4j should be accessible at:
# URI: bolt://localhost:7687
# User: neo4j
# Password: password
```

6. **Run the application**

```bash
./start.sh
# Or directly: python main.py
```

## 📖 Usage

### Interactive Mode

The application starts in interactive mode with a rich CLI interface:

```
Query: What is RAG and how does it work?
```

The system will:
1. Extract keywords from your natural language query
2. Retrieve relevant documents from all three sources (vector, BM25, graph)
3. Apply fusion ranking (RRF algorithm) to combine results
4. Apply HITL re-ranking based on past feedback
5. Generate a comprehensive answer using your chosen LLM (Ollama or OpenAI)
6. Display the answer with source references
7. Ask if you want to provide feedback on which source was most helpful

### Example Queries

Natural language queries work seamlessly:
- "What is Neo4j?"
- "Explain vector databases"
- "Tell me about RAG systems"
- "How does BM25 work?"

### Commands

- **Enter any question** - Query the system
- `sample` - Show example queries
- `stats` - Display system statistics (documents count, HITL interactions)
- `reset` - Reset HITL feedback data
- `help` - Show help message
- `exit` - Exit the application

### HITL Feedback

After each query, you can select which document was most helpful (1-N). This selection:
- Boosts that document's ranking for similar future queries
- Learns patterns across related queries using fuzzy matching
- Improves system performance over time
- Is persisted in `hitl_feedback.json` across restarts

**Feedback Formula:**
```
score = base_score + (boost_factor × similarity × selection_count × recency)
```

### Switching LLM Providers

Change `LLM_PROVIDER` in `.env`:

```bash
# Use Ollama (local, free)
LLM_PROVIDER=ollama

# Use OpenAI (requires API key)
LLM_PROVIDER=openai
```

Restart the application to apply changes. See [SWITCHING_LLM_PROVIDERS.md](SWITCHING_LLM_PROVIDERS.md) for details.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              User Query (Natural Language)              │
│           "What is Neo4j?" → ["neo4j"]                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Agentic RAG Orchestrator (agent.py)            │
│     • Keyword Extraction for Graph Queries              │
│     • Parallel Multi-Source Retrieval                   │
│     • Result Deduplication                              │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Vector    │  │    BM25     │  │   Graph     │
│   Search    │  │   Search    │  │   Search    │
│  (ChromaDB) │  │  (rank-bm25)│  │   (Neo4j)   │
│             │  │             │  │             │
│ Sentence    │  │ Tokenized   │  │ Cypher      │
│ Embeddings  │  │ Keywords    │  │ Queries     │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │  Fusion Ranking     │
              │  (RRF Algorithm)    │
              │  k=60, ranks→scores │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  HITL Re-ranking    │
              │  (Implicit Feedback)│
              │  hitl_feedback.json │
              └─────────────────────┘
                         │
                         ▼
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐         ┌─────────────────┐
│  Ollama (Free)  │   OR    │  OpenAI (Cloud) │
│  llama3.1:8b    │         │  gpt-4-turbo    │
│  Local LLM      │         │  API Required   │
└─────────────────┘         └─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Final Answer      │
              │   + Feedback Loop   │
              └─────────────────────┘
```

### Key Components

- **ChromaDB**: Persistent vector store with sentence-transformers embeddings
- **Neo4j**: Graph database with entity relationships and Cypher queries
- **BM25**: Okapi BM25 probabilistic ranking for keyword matching
- **HITL Reranker**: Learns from selections, applies boost with decay
- **Fusion Ranking**: RRF combines diverse retrieval methods optimally
- **Dual LLM**: Ollama (local) or OpenAI (cloud) for answer generation

## 📁 Project Structure

```
.
├── Core Application
│   ├── agent.py                    # Main RAG orchestrator with fusion ranking
│   ├── vector_store.py             # ChromaDB vector database wrapper
│   ├── graph_store.py              # Neo4j graph database with keyword extraction
│   ├── bm25_retriever.py           # BM25 keyword search implementation
│   ├── hitl_reranker.py            # HITL re-ranking with implicit feedback
│   ├── config.py                   # Configuration management & validation
│   ├── sample_data.py              # Sample documents for testing
│   ├── main.py                     # CLI application entry point
│   └── start.sh                    # Convenience launcher script
│
├── Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   └── .env                        # Your configuration (not in git)
│
├── Docker & Deployment
│   ├── Dockerfile                  # Container image definition
│   ├── docker-compose.yml          # Full stack orchestration (Neo4j + Ollama + App)
│   └── .dockerignore               # Docker build exclusions
│
├── CI/CD Pipelines
│   ├── Jenkinsfile                 # Jenkins pipeline for AWS ECR
│   ├── .gitlab-ci.yml              # GitLab CI/CD pipeline for AWS ECR
│   └── ecr-iam-policy.json         # AWS IAM permissions for ECR
│
├── Documentation
│   ├── README.md                   # This file - main documentation
│   ├── DOCKER_GUIDE.md             # Complete Docker setup & usage
│   ├── JENKINS_ECR_SETUP.md        # Jenkins pipeline setup guide
│   ├── GITLAB_CI_SETUP.md          # GitLab CI/CD setup guide
│   ├── CI_CD_COMPARISON.md         # Jenkins vs GitLab comparison
│   ├── SETUP_COMPLETE.md           # Initial setup walkthrough
│   ├── SYSTEM_EXPLANATION.md       # Architecture deep dive
│   ├── FUSION_RANKING_EXPLAINED.md # RRF algorithm details
│   ├── SWITCHING_LLM_PROVIDERS.md  # Ollama vs OpenAI guide
│   └── OLLAMA_ADDED.md             # Ollama integration summary
│
└── Data Files (Created at runtime)
    ├── chroma_db/                  # Vector embeddings (persistent)
    └── hitl_feedback.json          # HITL learning data (persistent)
```

## 🔧 Configuration

Edit `.env` to customize the system:

### LLM Provider Settings

**Ollama (Default - Local & Free):**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
# Alternatives: llama2, mistral, codellama, etc.
```

**OpenAI (Cloud - Requires API Key):**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### Database Configuration

```bash
# Neo4j Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ChromaDB Vector Store
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Retrieval Settings

```bash
TOP_K_VECTOR=5          # Top results from vector search
TOP_K_BM25=5            # Top results from BM25
TOP_K_GRAPH=3           # Top results from graph search
FINAL_TOP_K=10          # Final number of results to return
```

### HITL Configuration

```bash
HITL_BOOST_FACTOR=2.0   # How much to boost selected documents (multiplier)
HITL_DECAY_FACTOR=0.95  # Decay rate for old feedback (0.0-1.0)
HITL_FEEDBACK_FILE=hitl_feedback.json
```

See [config.py](config.py) for all available options.

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

## 🎯 Key Components Explained

### Vector Store (ChromaDB)
- Stores document embeddings using `all-MiniLM-L6-v2` Sentence-BERT model
- Performs semantic similarity search with cosine distance
- Persistent storage in `./chroma_db` directory
- Returns top-k most semantically similar documents

### Graph Store (Neo4j)
- Stores documents as nodes with entity relationships
- **Intelligent keyword extraction** from natural language queries
- Enables graph traversal queries using Cypher
- Case-insensitive search with `toLower()` matching
- Captures semantic relationships between concepts

### BM25 Retriever
- Traditional probabilistic retrieval using Okapi BM25
- Excellent for exact keyword matching and rare terms
- Tokenizes text for better keyword recognition
- Complements semantic search methods

### HITL Re-ranker
- Records user selections as implicit feedback
- Boosts relevant documents for similar queries (fuzzy matching)
- Self-improving system over time with temporal decay
- Persistent across sessions via `hitl_feedback.json`

### Fusion Ranking (RRF)
- Reciprocal Rank Fusion with k=60 constant
- Combines ranks from diverse retrieval methods
- More robust than score averaging
- Formula: `score = Σ(1/(k + rank_i))`

See [FUSION_RANKING_EXPLAINED.md](FUSION_RANKING_EXPLAINED.md) for detailed RRF documentation.

## � Deployment & CI/CD

### Automated Builds to AWS ECR

This project includes CI/CD pipelines for automated Docker image builds:

#### Jenkins Pipeline

```bash
# See JENKINS_ECR_SETUP.md for detailed setup
1. Install Jenkins with Docker support
2. Configure AWS credentials
3. Create Pipeline job pointing to Jenkinsfile
4. Run build → Image pushed to ECR
```

**Features:**
- Builds on every push
- Tags with build number
- Automatic ECR push
- Build artifacts management

📖 **Full Guide**: [JENKINS_ECR_SETUP.md](JENKINS_ECR_SETUP.md)

#### GitLab CI/CD Pipeline

```bash
# See GITLAB_CI_SETUP.md for detailed setup
1. Push code to GitLab
2. Add AWS credentials to CI/CD variables
3. Enable GitLab Runner
4. Pipeline runs automatically
```

**Features:**
- Native GitLab integration
- Multi-stage builds
- Automatic verification
- Built-in artifact system

📖 **Full Guide**: [GITLAB_CI_SETUP.md](GITLAB_CI_SETUP.md)

#### Choosing Between Jenkins & GitLab

| Use Case | Recommended |
|----------|-------------|
| Already using Jenkins | **Jenkins** |
| Code on GitLab | **GitLab CI/CD** |
| Need flexibility | **Jenkins** |
| Want simplicity | **GitLab CI/CD** |
| Multiple Git providers | **Jenkins** |

📊 **Detailed Comparison**: [CI_CD_COMPARISON.md](CI_CD_COMPARISON.md)

### Pull & Run from ECR

After CI/CD build completes:

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    797240615162.dkr.ecr.us-east-1.amazonaws.com

# Pull the image
docker pull 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest

# Run it
docker run -it --rm \
    -e NEO4J_URI=bolt://host.docker.internal:7687 \
    -e LLM_PROVIDER=ollama \
    797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
```

### Deploy to Production

Use the ECR image in your deployment platform:

**Kubernetes:**
```yaml
spec:
  containers:
  - name: rag-app
    image: 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
```

**AWS ECS:**
```json
{
  "image": "797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest"
}
```

**Docker Compose:**
```yaml
services:
  rag-app:
    image: 797240615162.dkr.ecr.us-east-1.amazonaws.com/agentic_rag_with_re-ranker:latest
```

## �🔒 Security Notes

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
