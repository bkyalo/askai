import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
import openai
from config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, OPENAI_API_KEY

class VectorDB:
    def __init__(self):
        # Ensure the database directory exists
        os.makedirs(DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Using cosine similarity
        )
        
        # Initialize OpenAI client
        openai.api_key = OPENAI_API_KEY
        
        print(f"Initialized database at: {os.path.abspath(DB_PATH)}")
        print(f"Collection '{COLLECTION_NAME}' has {self.collection.count()} documents")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a given text using OpenAI's embedding model"""
        try:
            response = openai.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector database"""
        if not documents:
            print("No documents to add")
            return
            
        print(f"Adding {len(documents)} documents to the database...")
        
        # Process documents in smaller batches to avoid timeouts
        batch_size = 20
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            ids = []
            embeddings = []
            metadatas = []
            texts = []
            
            for j, doc in enumerate(batch):
                try:
                    # Generate embedding for each document
                    embedding = self.get_embedding(doc['text'])
                    if embedding is None:
                        print(f"Skipping document {i+j} - failed to generate embedding")
                        continue
                        
                    doc_id = f"doc_{i+j}"
                    ids.append(doc_id)
                    embeddings.append(embedding)
                    metadatas.append({"source": doc.get('source', 'unknown')})
                    texts.append(doc['text'])
                    
                except Exception as e:
                    print(f"Error processing document {i+j}: {str(e)}")
                    continue
            
            # Add batch to collection
            if ids:
                try:
                    self.collection.upsert(
                        ids=ids,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        documents=texts
                    )
                    print(f"Added batch {i//batch_size + 1} - {len(ids)} documents")
                except Exception as e:
                    print(f"Error adding batch {i//batch_size + 1}: {str(e)}")
        
        # Verify the final count
        final_count = self.collection.count()
        print(f"Database now contains {final_count} documents")
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents to the query"""
        # Get query embedding
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i].get('source', 'unknown'),
                'score': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results

# Initialize a global instance of the vector database
db = VectorDB()
