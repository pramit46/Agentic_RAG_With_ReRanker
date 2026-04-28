"""
Test script to verify all components are working
This tests each component individually before running the full application
"""
import sys

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    try:
        import chromadb
        print("  ✓ chromadb")
        
        import sentence_transformers
        print("  ✓ sentence-transformers")
        
        import neo4j
        print("  ✓ neo4j")
        
        from rank_bm25 import BM25Okapi
        print("  ✓ rank-bm25")
        
        import openai
        print("  ✓ openai")
        
        import langchain
        print("  ✓ langchain")
        
        from rich.console import Console
        print("  ✓ rich")
        
        print("\n✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}\n")
        return False

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import config
        print(f"  ✓ Config loaded")
        print(f"  ↳ Neo4j URI: {config.NEO4J_URI}")
        print(f"  ↳ Chroma directory: {config.CHROMA_PERSIST_DIRECTORY}")
        print(f"  ↳ OpenAI key configured: {'Yes' if config.OPENAI_API_KEY else 'No (add to .env)'}")
        print("\n✅ Configuration loaded!\n")
        return True
    except Exception as e:
        print(f"\n❌ Config error: {e}\n")
        return False

def test_vector_store():
    """Test ChromaDB vector store"""
    print("Testing Vector Store (ChromaDB)...")
    try:
        from vector_store import VectorStore
        
        vs = VectorStore()
        print(f"  ✓ Vector store initialized")
        print(f"  ↳ Collection: {vs.collection_name}")
        print(f"  ↳ Documents: {vs.get_collection_count()}")
        
        print("\n✅ Vector store working!\n")
        return True
    except Exception as e:
        print(f"\n❌ Vector store error: {e}\n")
        return False

def test_neo4j():
    """Test Neo4j connection"""
    print("Testing Graph Store (Neo4j)...")
    try:
        from graph_store import GraphStore
        
        gs = GraphStore()
        print(f"  ✓ Neo4j connected")
        gs.close()
        
        print("\n✅ Neo4j connection successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Neo4j error: {e}")
        print(f"  ↳ Make sure Neo4j is running at localhost:7474")
        print(f"  ↳ Check credentials (neo4j/password)\n")
        return False

def test_bm25():
    """Test BM25 retriever"""
    print("Testing BM25 Retriever...")
    try:
        from bm25_retriever import BM25Retriever
        
        bm25 = BM25Retriever()
        print(f"  ✓ BM25 initialized")
        print(f"  ↳ Documents: {bm25.get_document_count()}")
        
        print("\n✅ BM25 retriever working!\n")
        return True
    except Exception as e:
        print(f"\n❌ BM25 error: {e}\n")
        return False

def test_hitl():
    """Test HITL re-ranker"""
    print("Testing HITL Re-ranker...")
    try:
        from hitl_reranker import HITLReranker
        
        hitl = HITLReranker()
        stats = hitl.get_statistics()
        print(f"  ✓ HITL initialized")
        print(f"  ↳ Unique queries: {stats['unique_queries']}")
        print(f"  ↳ Total interactions: {stats['total_interactions']}")
        
        print("\n✅ HITL re-ranker working!\n")
        return True
    except Exception as e:
        print(f"\n❌ HITL error: {e}\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AGENTIC RAG SYSTEM - COMPONENT TESTS")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Vector Store", test_vector_store()))
    results.append(("Neo4j", test_neo4j()))
    results.append(("BM25", test_bm25()))
    results.append(("HITL", test_hitl()))
    
    # Summary
    print("="*60)
    print("  TEST SUMMARY")
    print("="*60 + "\n")
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n  Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nRun: ./venv/bin/python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
