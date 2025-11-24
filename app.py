from src.data_loader import DataLoader
from src.stopwords import StopwordRemover


if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_documents()
    stopword_remover = StopwordRemover(document_text)
    cleaned_text = stopword_remover.remove_stopwords()
    print(f"[INFO] Cleaned document text length: {len(cleaned_text)} characters")