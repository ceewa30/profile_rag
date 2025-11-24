from src.data_loader import DataLoader
from src.stopwords import StopwordRemover
import re

class DataCleaner:
    def __init__(self, text: str) -> str:
        self.text = text

    def clean_text(self) -> str:
        text = re.sub(r'\s+', ' ',self.text) # Replace multiple whitespace with single space
        text = re.sub(r'[^\w\s]', ' ', text) # Remove special characters
        return text.strip()



if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document = data_loader.load_all_documents()

    stopword_remover = StopwordRemover(document)
    cleaned_text = stopword_remover.remove_stopwords()

    data_cleaner = DataCleaner(cleaned_text)
    cleaned_document_text = data_cleaner.clean_text()