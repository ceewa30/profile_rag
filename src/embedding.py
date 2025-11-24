import re
from typing import List, Any
import numpy as np
from src.data_clean import DataCleaner
from src.data_loader import DataLoader
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class EmbeddingProcessor:
    def __init__(self, model_name: str = "text-embedding-ada-002", chunk_size: int = 1000, overlap: int = 200):
        self.model_name = model_name
        self.client = OpenAI()
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.overlap
        return chunks

    def get_embedding(self, chunks: List[Any]) -> np.ndarray:
        embeddings = []
        for chunk in chunks:
            response = self.client.embeddings.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
            embeddings.append(response.data[0].embedding)
        return np.array(embeddings)



if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document = data_loader.load_all_documents()
    data_cleaner = DataCleaner(document)
    cleaned_document = data_cleaner.clean_text()
    embedding_pipeline = EmbeddingProcessor()
    text_chunks = embedding_pipeline.chunk_text(cleaned_document)
    embeddings = embedding_pipeline.get_embedding(text_chunks)
    print(f"Generated {len(embeddings)} embeddings for {len(text_chunks)} text chunks.")
    print(embeddings)