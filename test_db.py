# test_db.py
from database import db
import os

print("=== Testing Database Connection ===")
print(f"Database path: {os.path.abspath('chroma_db')}")

# List all collections
print("\nCollections in database:")
print(db.client.list_collections())

# Try to access the collection
try:
    count = db.collection.count()
    print(f"\nNumber of documents in collection: {count}")
except Exception as e:
    print(f"\nError accessing collection: {str(e)}")