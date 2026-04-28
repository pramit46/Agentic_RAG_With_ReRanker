"""
Demo script to show system output WITHOUT needing OpenAI key
This demonstrates the retrieval and re-ranking components only
"""
from vector_store import VectorStore
from graph_store import GraphStore
from bm25_retriever import BM25Retriever
from hitl_reranker import HITLReranker
from sample_data import get_sample_documents
from rich.console import Console
from rich.table import Table

console = Console()

def demo_retrieval_only():
    """Demonstrate retrieval without LLM"""
    
    console.print("\n[bold cyan]🔍 RETRIEVAL DEMO (No OpenAI Key Needed)[/bold cyan]\n")
    
    # Initialize components
    vector_store = VectorStore()
    bm25 = BM25Retriever()
    hitl = HITLReranker()
    
    # Load sample data
    docs = get_sample_documents()
    console.print(f"Loading {len(docs)} sample documents...")
    vector_store.add_documents(docs)
    bm25.add_documents(docs)
    
    # Test query
    query = "What is RAG?"
    console.print(f"\n[bold]Query:[/bold] {query}\n")
    
    # Vector search
    console.print("[cyan]1. Vector Search Results:[/cyan]")
    vector_results = vector_store.similarity_search(query, top_k=3)
    for i, doc in enumerate(vector_results, 1):
        console.print(f"  {i}. Score: {doc['score']:.3f}")
        console.print(f"     {doc['text'][:100]}...\n")
    
    # BM25 search
    console.print("[cyan]2. BM25 Search Results:[/cyan]")
    bm25_results = bm25.search(query, top_k=3)
    for i, doc in enumerate(bm25_results, 1):
        console.print(f"  {i}. Score: {doc['score']:.3f}")
        console.print(f"     {doc['text'][:100]}...\n")
    
    # Combine and rerank
    all_docs = vector_results + bm25_results
    reranked = hitl.rerank(query, all_docs)
    
    console.print("[cyan]3. Combined & Re-ranked Results:[/cyan]")
    table = Table(show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Source", width=12)
    table.add_column("Score", width=10)
    table.add_column("Preview", width=60)
    
    for i, doc in enumerate(reranked[:5], 1):
        table.add_row(
            str(i),
            doc.get("source", "unknown"),
            f"{doc['score']:.3f}",
            doc['text'][:80] + "..."
        )
    
    console.print(table)
    
    console.print("\n[bold green]✓ Retrieval & Re-ranking working![/bold green]")
    console.print("\n[yellow]Note: To get LLM-generated answers, add OPENAI_API_KEY to .env[/yellow]\n")

if __name__ == "__main__":
    demo_retrieval_only()
