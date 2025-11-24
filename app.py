from src.data_loader import DataLoader
from src.stopwords import StopwordRemover
from src.data_clean import DataCleaner


if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_documents()
    stopword_remover = StopwordRemover(document_text)
    cleaned_text = stopword_remover.remove_stopwords()
    data_cleaner = DataCleaner(cleaned_text)
    cleaned_text = data_cleaner.clean_text()
    print(f"[INFO] Cleaned document : {cleaned_text} characters")