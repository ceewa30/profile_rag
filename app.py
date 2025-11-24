from src.data_loader import DataLoader
from src.stopwords import StopwordRemover
from src.data_clean import DataCleaner
from src.embedding import EmbeddingProcessor

if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_documents()
    stopword_remover = StopwordRemover(document_text)
    cleaned_text = stopword_remover.remove_stopwords()
    data_cleaner = DataCleaner(cleaned_text)
    cleaned_text = data_cleaner.clean_text()
    embedding_processor = EmbeddingProcessor()
    text_chunks = embedding_processor.chunk_text(cleaned_text)
    embeddings = embedding_processor.get_embedding(text_chunks)
    print(f"[INFO] Generated {len(embeddings)} embeddings for {len(text_chunks)} text chunks.")