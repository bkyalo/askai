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
    """Load documents into the database"""
    print("\n=== Loading Documents ===")
    from document_loader import DocumentLoader
    
    try:
        # Clear existing database
        print("Clearing existing database...")
        db.collection.delete(where={"source": {"$ne": ""}})
        
        # Load documents
        loader = DocumentLoader()
        documents = loader.load_directory('documents')
        print(f"\nLoaded {len(documents)} document chunks")
        
        # Add to database
        print("Adding documents to the database...")
        db.add_documents(documents)
        
        # Verify count
        count = db.collection.count()
        print(f"\nSuccessfully added {count} document chunks to the database.")
        print(f"Documents in database: {count}")
        
        # Print sample of added documents
        print("\nSample of added documents:")
        results = db.collection.get(limit=3)
        for i, (text, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            print(f"\n--- Document {i+1} ---")
            print(f"Source: {metadata['source']}")
            print(f"Content: {text[:200]}..." if len(text) > 200 else f"Content: {text}")
            
    except Exception as e:
        print(f"Error loading documents: {e}")
        raise

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
        "Malaria symptoms",
        "health guidelines",
        "prevention measures"
    ]
    
    # Load documents if database is empty
    if db.collection.count() == 0:
        load_documents()
    
    # Test search with queries
    for query in test_queries:
        test_search(query)