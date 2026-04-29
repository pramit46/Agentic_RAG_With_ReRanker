# 🐳 Docker Deployment Guide

This guide explains how to run the Agentic RAG application using Docker.

## 📦 What's Included

The Docker setup includes:
- **Agentic RAG Application** - Your main Python application
- **Neo4j** - Graph database (Community Edition)
- **Ollama** - Local LLM service with Llama 3.1 8B model
- **Persistent Volumes** - For ChromaDB, Neo4j data, and HITL feedback

## 🚀 Quick Start

### 1. Build and Start All Services

```bash
docker-compose up -d
```

This will:
- Start Neo4j on ports 7474 (HTTP) and 7687 (Bolt)
- Start Ollama on port 11434 and pull llama3.1:8b model
- Build and start the RAG application

### 2. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag-app
docker-compose logs -f neo4j
docker-compose logs -f ollama
```

### 3. Access the Application

```bash
# Attach to the interactive terminal
docker attach rag-application
```

Then use the application normally:
- Type your queries
- Use commands: `stats`, `reset`, `help`, `exit`

### 4. Detach Without Stopping

Press: `Ctrl+P` then `Ctrl+Q`

### 5. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data!)
docker-compose down -v
```

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  # Switch to OpenAI (requires API key)
  - LLM_PROVIDER=openai
  - OPENAI_API_KEY=your-key-here
  
  # Use different Ollama model
  - OLLAMA_MODEL=llama2
  
  # Adjust Neo4j credentials
  - NEO4J_PASSWORD=your-secure-password
```

### Use Your Own OpenAI Key

```bash
# Set in your shell
export OPENAI_API_KEY=sk-...

# Run with the key
docker-compose up -d
```

## 📊 Access Neo4j Browser

Open in your browser: http://localhost:7474

- **Username**: `neo4j`
- **Password**: `password`

## 🔍 Troubleshooting

### Check Service Health

```bash
docker-compose ps
```

### Restart a Service

```bash
docker-compose restart rag-app
docker-compose restart neo4j
docker-compose restart ollama
```

### View Ollama Models

```bash
docker exec -it rag-ollama ollama list
```

### Manual Model Pull

```bash
docker exec -it rag-ollama ollama pull llama3.1:8b
```

### Clear and Rebuild

```bash
# Stop everything
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 📁 Data Persistence

Data is persisted in Docker volumes:
- `neo4j_data` - Graph database
- `chroma_data` - Vector embeddings
- `ollama_data` - Downloaded models
- `hitl_feedback.json` - HITL learning (bind mount)

### Backup Data

```bash
# Backup ChromaDB
docker cp rag-application:/app/chroma_db ./backup_chroma_db

# Backup Neo4j
docker exec rag-neo4j neo4j-admin database dump neo4j --to-path=/backups
docker cp rag-neo4j:/backups ./backup_neo4j
```

## 🎯 Production Considerations

For production deployment:

1. **Use secrets** for passwords (Docker Swarm or Kubernetes)
2. **Set resource limits** in docker-compose.yml
3. **Use external volumes** for backups
4. **Enable authentication** on all services
5. **Use HTTPS** with reverse proxy (nginx, Traefik)
6. **Monitor** with Prometheus/Grafana

### Resource Limits Example

```yaml
services:
  rag-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🔄 Development Mode

Mount your code for live editing:

```yaml
services:
  rag-app:
    volumes:
      - .:/app  # Add this line
      - chroma_data:/app/chroma_db
```

Then restart when you make changes:
```bash
docker-compose restart rag-app
```

## 🌐 API Mode (Future)

To expose the app as an API service, modify `Dockerfile`:

```dockerfile
# Install FastAPI
RUN pip install fastapi uvicorn

# Change CMD
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then access at: http://localhost:8000

---

**Built with:** Python 3.12, Neo4j 5.18, Ollama, ChromaDB
