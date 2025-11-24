import nltk
from nltk.corpus import stopwords
from src.data_loader import DataLoader

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except ntlk.downloader.DownloadError:
    nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

class StopwordRemover:
    def __init__(self, text: str):
        self.text = text

    def remove_stopwords(self) -> str:
        """
        Remove English stopwords from the given text.
        """
        # Tokenize (split into words) and convert to lowercase for effective filtering
        words = self.text.lower().split()
        filtered_words = [word for word in words if word not in STOPWORDS]
        return ' '.join(filtered_words)


if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document = data_loader.load_all_documents()
    stopword_remover = StopwordRemover(document)
    cleaned_text = stopword_remover.remove_stopwords()

    print(cleaned_text)
