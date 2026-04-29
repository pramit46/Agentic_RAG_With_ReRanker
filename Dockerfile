# Agentic RAG Application Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY .env.example .env

# Create directories for persistent data
RUN mkdir -p /app/chroma_db /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# Expose port (if needed for future API)
EXPOSE 8000

# Default command - run the interactive application
CMD ["python", "main.py"]
