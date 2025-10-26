#!/bin/bash

# setup_database.sh
# This script sets up the database by loading documents and testing the search functionality

echo "=== Setting up AskAI Database ==="

# Clear existing database
echo "Clearing existing database..."
rm -rf chroma_db/

# Run the Python script to load documents and test search
echo "Loading documents and testing search..."
python -c "
from database import db
from document_loader import DocumentLoader

# Load documents
print('\n=== Loading documents ===')
loader = DocumentLoader()
documents = loader.load_directory('documents')
print(f'✅ Loaded {len(documents)} document chunks')

# Add to database
print('\n=== Adding to database ===')
db.add_documents(documents)
print('✅ Documents added to database')

# Test search
print('\n=== Testing search ===')
queries = [
    'What are the symptoms of COVID-19?',
    'How to prevent malaria?',
    'General health guidelines'
]

for query in queries:
    print(f'\n🔍 Searching for: {query}')
    results = db.search(query, k=2)
    print(f'Found {len(results)} results:')
    for i, doc in enumerate(results, 1):
        print(f'\n--- Result {i} ---')
        print(f'Source: {doc.get(\"source\", \"Unknown\")}')
        print(f'Content: {doc[\"text\"][:200]}...')
"

echo "\n=== Setup Complete ==="
echo "You can now run the bot with: python app.py"
