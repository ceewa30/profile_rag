import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from chromadb.utils import embedding_functions
from src.data_clean import DataCleaner
from src.stopwords import StopwordRemover
import numpy as np
from typing import List, Any
from src.embedding import EmbeddingProcessor
#
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

class ChromaStore:
    def __init__(self, persist_directory: str = "chroma_store", collection_name: str = "documents", embedding_function=ef, chunk_size: int = 1000, overlap: int = 200):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_model = embedding_function
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_processor = EmbeddingProcessor(model_name=self.embedding_model, chunk_size=self.chunk_size, overlap=self.overlap)
        self.chroma_client = chromadb.PersistentClient(
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
            path=self.persist_directory,  # Specify the directory for persistent storage
            settings=Settings(
                allow_reset=True  # Example setting, adjust as needed
            )
        )
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name, embedding_function=None)


    def build_from_documents(self, documents: List[Any]) -> str:
        print(f"[INFO] Building Chroma store from {len(documents)} raw documents...")
        stopword_remover = StopwordRemover(documents)
        cleaned_text = stopword_remover.remove_stopwords()
        data_cleaner = DataCleaner(cleaned_text)
        cleaned_document = data_cleaner.clean_text()
        chunks = self.embedding_processor.chunk_text(cleaned_document)
        embeddings = self.embedding_processor.get_embedding(chunks)
        ids = [f"id_{i}" for i in range(len(chunks))]
        metadatas = [{"text": chunk} for chunk in chunks]
        self.add_embeddings(ids=ids, documents=chunks, metadatas=metadatas, embeddings=np.array(embeddings).astype('float32'))
        print(f"[INFO] Chroma store built and persisted at {self.persist_directory}")

    def add_embeddings(self, embeddings: np.array, ids: List[str], documents: List[str], metadatas: List[Any] = None):
        dim = embeddings.shape[1]
        print(f"[INFO] Adding {embeddings.shape[0]} embeddings to the Chroma store with dimension {dim}...")
        if metadatas is None:
            metadatas = [{"text": f"embedding_{i}"} for i in range(len(embeddings))]
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def load(self):
        print(f"[INFO] Loading Chroma store from {self.persist_directory}...")
        db_path = "/Users/sivakumars/Documents/Agentic_AI/chroma_store"
        self.chroma_client = chromadb.PersistentClient(
            path=db_path
        )
        self.collection = self.chroma_client.get_collection(name=self.collection_name)
        print(f"[INFO] Chroma store loaded from {self.collection}.")

    def query(self, query_text="query_text", n_results="n_results") -> List[Any]:
        query_embedding = self.embedding_processor.get_embedding([query_text])
        results = self.collection.query(query_embeddings=query_embedding, n_results=n_results)
        return results


if __name__ == "__main__":
    from data_loader import DataLoader
    data_loader = DataLoader("../me")
    document = data_loader.load_all_documents()
    chroma_store = ChromaStore("chroma_store")
    chroma_store.build_from_documents(document)
    query_text = "Tell me about yourself."
    results = chroma_store.query(query_text=query_text, n_results=1)
    for result in results['metadatas']:
        print(result[0]['text'])
