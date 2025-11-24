from src.data_loader import DataLoader


if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_documents()
    print(f"[INFO] Loaded document text length: {len(document_text)} characters")