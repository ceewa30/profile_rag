from src.data_loader import DataLoader
from src.stopwords import StopwordRemover
from src.data_clean import DataCleaner
from src.chromastore import ChromaStore

if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_documents()
    stopword_remover = StopwordRemover(document_text)
    cleaned_text = stopword_remover.remove_stopwords()
    data_cleaner = DataCleaner(cleaned_text)
    cleaned_text = data_cleaner.clean_text()
    chroma_store = ChromaStore("chroma_store")
    chroma_store.build_from_documents([cleaned_text])
    query_text = "Tell me about yourself."
    results = chroma_store.query(query_text=query_text, n_results=1)
    for result in results['metadatas']:
        print(result)