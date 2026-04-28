"""
Main Application Entry Point
Interactive CLI for the Agentic RAG system
"""
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from agent import AgenticRAG
from sample_data import get_sample_documents, get_sample_queries
from config import config
import time

# Initialize rich console for beautiful CLI output
console = Console()

def print_banner():
    """
    Display application banner
    """
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         🤖 AGENTIC RAG WITH HITL RE-RANKING 🤖           ║
    ║                                                           ║
    ║      Vector DB + Graph DB + BM25 + HITL System          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def setup_environment():
    """
    Check and setup the environment
    Creates .env file if it doesn't exist
    """
    env_file = Path(".env")
    
    if not env_file.exists():
        console.print("\n⚠️  No .env file found!", style="bold yellow")
        console.print("Creating .env file from example...\n")
        
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            console.print("✓ Created .env file", style="green")
            console.print("\n⚠️  Please edit .env and add your OPENAI_API_KEY\n", style="bold yellow")
            
            # Ask for API key
            if Confirm.ask("Would you like to enter your OpenAI API key now?"):
                api_key = Prompt.ask("Enter your OpenAI API key", password=True)
                
                # Update .env file
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                with open(env_file, 'w') as f:
                    for line in lines:
                        if line.startswith("OPENAI_API_KEY="):
                            f.write(f"OPENAI_API_KEY={api_key}\n")
                        else:
                            f.write(line)
                
                console.print("✓ Updated .env with API key\n", style="green")
                
                # Reload config
                from importlib import reload
                import config as config_module
                reload(config_module)

def initialize_system():
    """
    Initialize the Agentic RAG system with sample data
    
    Returns:
        AgenticRAG instance
    """
    console.print("\n[bold]Initializing Agentic RAG System...[/bold]\n")
    
    try:
        # Validate configuration
        config.validate()
        
        # Initialize RAG system
        rag_system = AgenticRAG()
        
        # Check if we need to load sample data
        stats = rag_system.get_statistics()
        
        if stats["vector_store_count"] == 0:
            console.print("[yellow]No documents found in the system.[/yellow]")
            
            if Confirm.ask("\nWould you like to load sample documents?", default=True):
                console.print("\n[bold]Loading sample documents...[/bold]\n")
                documents = get_sample_documents()
                rag_system.add_documents(documents)
                console.print(f"[green]✓ Loaded {len(documents)} sample documents[/green]\n")
        else:
            console.print(f"[green]✓ Found {stats['vector_store_count']} documents in the system[/green]\n")
        
        return rag_system
        
    except ValueError as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]\n")
        sys.exit(1)

def display_results(result: dict):
    """
    Display query results in a formatted way
    
    Args:
        result: Result dictionary from RAG system
    """
    # Display answer
    console.print("\n[bold cyan]📝 Answer:[/bold cyan]\n")
    answer_md = Markdown(result["answer"])
    console.print(Panel(answer_md, border_style="cyan"))
    
    # Display supporting documents
    documents = result["documents"]
    
    if documents:
        console.print(f"\n[bold]📚 Supporting Documents ({len(documents)}):[/bold]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Source", width=15)
        table.add_column("Score", width=10)
        table.add_column("Boosted", width=10)
        table.add_column("Preview", width=60)
        
        for i, doc in enumerate(documents, 1):
            source = doc.get("source", "unknown")
            score = doc.get("score", 0)
            boosted = "★ YES" if doc.get("boosted", False) else "No"
            text = doc.get("text", "")
            preview = text[:100] + "..." if len(text) > 100 else text
            
            table.add_row(
                str(i),
                source,
                f"{score:.3f}",
                boosted,
                preview
            )
        
        console.print(table)
    
    # Display metadata
    console.print(f"\n[dim]⏱️  Generation time: {result.get('generation_time', 0):.2f}s[/dim]\n")

def handle_user_feedback(rag_system: AgenticRAG, query: str, documents: list):
    """
    Handle user feedback for HITL learning
    
    Args:
        rag_system: RAG system instance
        query: The query that was asked
        documents: List of documents that were returned
    """
    if not documents:
        return
    
    console.print("\n[bold yellow]📊 Human-in-the-Loop Feedback[/bold yellow]")
    console.print("[dim]Your selections help improve future rankings![/dim]\n")
    
    if Confirm.ask("Would you like to select a particularly helpful document?", default=False):
        console.print("\nWhich document was most helpful? (Enter the document number)")
        
        doc_num = IntPrompt.ask(
            "Document #",
            default=1,
            choices=[str(i) for i in range(1, len(documents) + 1)]
        )
        
        # Record selection (convert to 0-based index)
        rag_system.record_user_selection(query, doc_num - 1, documents)
        
        console.print("\n[green]✓ Thank you! Your feedback has been recorded.[/green]")
        console.print("[dim]This document will be ranked higher for similar queries in the future.[/dim]\n")

def interactive_mode(rag_system: AgenticRAG):
    """
    Run the interactive query loop
    
    Args:
        rag_system: Initialized RAG system
    """
    console.print("\n[bold green]🚀 Ready! Enter your queries or type 'help' for commands.[/bold green]\n")
    
    while True:
        try:
            # Get user input
            query = Prompt.ask("\n[bold cyan]Query[/bold cyan]")
            
            # Handle special commands
            if query.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break
            
            elif query.lower() == 'help':
                show_help()
                continue
            
            elif query.lower() == 'stats':
                show_statistics(rag_system)
                continue
            
            elif query.lower() == 'sample':
                show_sample_queries()
                continue
            
            elif query.lower() == 'reset':
                if Confirm.ask("\n⚠️  Are you sure you want to reset HITL feedback?", default=False):
                    rag_system.hitl_reranker.reset()
                    console.print("[green]✓ HITL feedback reset[/green]\n")
                continue
            
            # Process query
            if query.strip():
                console.print("\n[bold]Processing your query...[/bold]\n")
                
                start_time = time.time()
                result = rag_system.query(query)
                total_time = time.time() - start_time
                
                # Display results
                display_results(result)
                
                # Get user feedback
                handle_user_feedback(rag_system, query, result["documents"])
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        
        except Exception as e:
            console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
            continue

def show_help():
    """
    Display help information
    """
    help_text = """
    [bold cyan]Available Commands:[/bold cyan]
    
    • Enter any question to query the system
    • [bold]sample[/bold]  - Show example queries
    • [bold]stats[/bold]   - Display system statistics
    • [bold]reset[/bold]   - Reset HITL feedback data
    • [bold]help[/bold]    - Show this help message
    • [bold]exit[/bold]    - Exit the application
    
    [bold cyan]How it works:[/bold cyan]
    
    1. Your query is processed through multiple retrieval methods:
       • Vector Search (semantic similarity)
       • BM25 (keyword matching)
       • Graph Traversal (relationship-based)
    
    2. Results are fused and re-ranked using HITL feedback
    
    3. When you select a helpful document, the system learns
       to rank similar documents higher in future queries
    """
    console.print(Panel(help_text, border_style="blue"))

def show_sample_queries():
    """
    Display sample queries
    """
    queries = get_sample_queries()
    
    console.print("\n[bold cyan]Sample Queries:[/bold cyan]\n")
    
    for i, query in enumerate(queries, 1):
        console.print(f"  {i}. {query}")
    
    console.print()

def show_statistics(rag_system: AgenticRAG):
    """
    Display system statistics
    
    Args:
        rag_system: RAG system instance
    """
    stats = rag_system.get_statistics()
    
    console.print("\n[bold cyan]📊 System Statistics:[/bold cyan]\n")
    
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")
    
    table.add_row("Vector Store Documents", str(stats["vector_store_count"]))
    table.add_row("BM25 Index Documents", str(stats["bm25_index_count"]))
    table.add_row("HITL Unique Queries", str(stats["hitl_stats"]["unique_queries"]))
    table.add_row("HITL Unique Selections", str(stats["hitl_stats"]["unique_selections"]))
    table.add_row("HITL Total Interactions", str(stats["hitl_stats"]["total_interactions"]))
    
    console.print(table)
    console.print()

def main():
    """
    Main application entry point
    """
    # Print banner
    print_banner()
    
    # Setup environment
    setup_environment()
    
    # Initialize system
    rag_system = initialize_system()
    
    try:
        # Run interactive mode
        interactive_mode(rag_system)
    
    finally:
        # Cleanup
        console.print("\n[dim]Closing connections...[/dim]")
        rag_system.close()
        console.print("[dim]✓ All connections closed[/dim]\n")

if __name__ == "__main__":
    main()
