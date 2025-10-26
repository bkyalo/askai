# test_knowledge.py
import os
from database import db
from config import OPENAI_API_KEY, DB_PATH
import openai

def check_database():
    print("\n=== Database Information ===")
    print(f"Database path: {os.path.abspath(DB_PATH)}")
    
    try:
        # Get the collection that was already created in db.py
        collection = db.collection
        
        # Get document count
        count = collection.count()
        print(f"Documents in collection: {count}")
        
        # List first few documents if any
        if count > 0:
            print("\nSample document chunks:")
            results = collection.peek(limit=2)
            for i, doc in enumerate(results['documents'][0][:2], 1):
                print(f"\n--- Chunk {i} ---")
                print(f"Content: {doc[:200]}...")  # First 200 chars of first 2 docs
    except Exception as e:
        print(f"Error accessing database: {e}")
        print("Trying to reload documents...")
        load_documents()
        
def load_documents():
    """Load documents into the database if not already loaded"""
    print("\n=== Loading Documents ===")
    from document_loader import DocumentLoader
    
    try:
        loader = DocumentLoader()
        documents = loader.load_directory('documents')
        print(f"Loaded {len(documents)} document chunks")
        
        # Add to database
        db.add_documents(documents)
        print("Documents added to the knowledge base.")
    except Exception as e:
        print(f"Error loading documents: {e}")

def test_search(query):
    print(f"\n=== Testing search for: '{query}' ===")
    results = db.search(query, k=3)
    
    if not results:
        print("No results found. The knowledge base might be empty or the query didn't match any content.")
        return
        
    print(f"Found {len(results)} results:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {doc.get('source', 'Unknown')}")
        print(f"Content: {doc['text'][:300]}...")  # Show first 300 chars

if __name__ == "__main__":
    # Disable ChromaDB telemetry
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    
    # Check database status
    check_database()
    
    # Test with some queries
    test_queries = [
        "COVID-19 symptoms",
        "health guidelines",
        "prevention measures"
    ]
    
    # Load documents if database is empty
    if db.collection.count() == 0:
        load_documents()
    
    # Test search with queries
    for query in test_queries:
        test_search(query)