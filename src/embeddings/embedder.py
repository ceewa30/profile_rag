import re
from typing import List, Any
import numpy as np  # pyright: ignore[reportMissingImports]
import os
import sys

# Dynamically add the "src" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.data_loader import DataLoader
from chunking.text_splitter import TextSplitter
from openai import OpenAI  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv(override=True)

class EmbeddingProcessor:
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.client = OpenAI()

    def get_embedding(self, chunks: List[str]) -> np.ndarray:
        """Sends all chunks in a single batched API call for maximum speed."""
        if not chunks:
            return np.empty((0, 0))
            
        # Send the entire list of chunks at once
        response = self.client.embeddings.create(
            input=chunks,
            model=self.model_name
        )
        
        # Extract the embeddings in the exact order they were sent
        embeddings = [data.embedding for data in response.data]
        return np.array(embeddings)


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