import re
from typing import List, Any
import numpy as np  # pyright: ignore[reportMissingImports]
import os
import sys

# Dynamically add the "src" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.data_loader import DataLoader
from chunking.text_splitter import TextSplitter
from embeddings.embedder import EmbeddingProcessor
import chromadb  # pyright: ignore[reportMissingImports]
from chromadb.config import Settings  # pyright: ignore[reportMissingImports]
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, db_path: str, collection_name: str = "profile_collection"):
        """Initializes a local persistent ChromaDB database on disk."""
        self.client = chromadb.PersistentClient(path=db_path)
        # Get or create the vector collection
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, chunks: List[str], embeddings: list, ids: List[str] = None, metadatas: List[Dict[str, Any]] = None):
        """Stores text chunks, their pre-computed embeddings, and metadata."""
        if not chunks:
            return
            
        # Automatically generate string IDs if none are provided
        if ids is None:
            ids = [str(i) for i in range(len(chunks))]
            
        # Native chroma client accepts raw python list of floats for embeddings
        embeddings_list = embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings

        self.collection.add(
            embeddings=embeddings_list,
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Successfully indexed {len(chunks)} chunks into ChromaDB.")

    def query_similarity(self, query_embedding: list, top_k: int = 3) -> Dict[str, Any]:
        """Queries the vector database using a pre-computed query embedding."""
        embedding_list = query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding
        
        results = self.collection.query(
            query_embeddings=[embedding_list],
            n_results=top_k
        )
        return results


if __name__ == "__main__":
    # Load all documents from "me" directory
    import os
    
    # 1. Initialize your splitter with customized boundaries
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

    # 2. Resolve absolute paths dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Inside /src/chunking/
    
    # FIX: Go up TWO levels to reach the root /profile_rag/, then down into /me/
    target_path = os.path.abspath(os.path.join(script_dir, "..", "..", "me"))

    # 3. Pass the resolved absolute path to your loader
    data_loader = DataLoader(target_path)
    documents = data_loader.load_all_documents()
    all_profile_chunks = []
    
    # If load_all_documents returns a list of strings or doc objects
    if isinstance(documents, list):
        for doc in documents:
            # Extract raw string text if it's an object, or use directly if it's already a string
            raw_text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            all_profile_chunks.extend(splitter.split_text(raw_text))
            
    # Fallback if it returns a single monolithic string
    elif isinstance(documents, str):
        all_profile_chunks = splitter.split_text(documents)

    # 5. Inspect and verify the final chunks
    print(f"Successfully generated {len(all_profile_chunks)} chunks.")
    for idx, chunk in enumerate(all_profile_chunks):
        print(f"\n--- Chunk {idx + 1} ---")
        print(chunk)
    embedding_pipeline = EmbeddingProcessor()
    embeddings = embedding_pipeline.get_embedding(all_profile_chunks)
    print(f"Generated {len(embeddings)} embeddings for {len(all_profile_chunks)} text chunks.")
    print(embeddings)

    db_storage_path = os.path.abspath(os.path.join(script_dir, "..", "..", "chroma_db"))
    
    # Initialize your local DB
    v_db = VectorStore(db_path=db_storage_path)
    
    # Store everything locally on disk
    v_db.add_documents(chunks=all_profile_chunks, embeddings=embeddings)
    
    print(f"ChromaDB persistent database successfully updated at: {db_storage_path}")