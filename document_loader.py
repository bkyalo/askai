import os
import PyPDF2
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Load and split a PDF file into chunks"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Extract text from PDF
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Prepare documents with metadata
        documents = []
        for chunk in chunks:
            documents.append({
                'text': chunk,
                'source': os.path.basename(file_path)
            })
            
        return documents
    
    def load_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """Load all PDF files from a directory"""
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Directory not found: {dir_path}")
            
        all_documents = []
        for filename in os.listdir(dir_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(dir_path, filename)
                try:
                    documents = self.load_pdf(file_path)
                    all_documents.extend(documents)
                    print(f"Loaded {len(documents)} chunks from {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        return all_documents

# Example usage:
if __name__ == "__main__":
    # Example: Load documents from a directory
    loader = DocumentLoader()
    documents = loader.load_directory("documents")  # Create a 'documents' folder and add your PDFs
    print(f"Total chunks loaded: {len(documents)}")
