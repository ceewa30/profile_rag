from pathlib import Path
from typing import List, Any
from PyPDF2 import PdfReader
from docx import Document

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_all_documents(self) -> List[Any]:
        """
        Load all supported files from the data directory and convert to OpenAI document structure.
        Supported file types: PDF, TXT, Word (.docx)
        """
        # Use project root data folder
        data_path = Path(self.data_dir).resolve()
        print(f"[DEBUG] Data path: {data_path}")
        documents = []

        # Load PDF files
        pdf_files = list(data_path.glob('**/*.pdf'))
        print(f"[DEBUG] Found PDF files: {pdf_files}")
        for pdf_file in pdf_files:
            print(f"[DEBUG] Processing PDF: {pdf_file}")
            try:
                reader = PdfReader(str(pdf_file))
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                documents.append({
                    "text": text,
                    "metadata": {"source": str(pdf_file)}
                })
            except Exception as e:
                print(f"[ERROR] Failed to process PDF {pdf_file}: {e}")

        # Load TXT files
        txt_files = list(data_path.glob('**/*.txt'))
        print(f"[DEBUG] Found TXT files: {txt_files}")
        for txt_file in txt_files:
            print(f"[DEBUG] Processing TXT: {txt_file}")
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                documents.append({
                    "text": text,
                    "metadata": {"source": str(txt_file)}
            })
            except Exception as e:
                print(f"[ERROR] Failed to process TXT {txt_file}: {e}")

        # Future: Add support for Word (.docx) files
        doc_files = list(data_path.glob('**/*.docx'))
        print(f"[DEBUG] Found DOCX files: {doc_files}")
        for doc_file in doc_files:
            print(f"[DEBUG] Processing DOCX: {doc_file}")
            try:
                with open(doc_file, 'rb') as f:
                    doc = Document(f)
                    text = "\n".join([para.text for para in doc.paragraphs])
                documents.append({
                    "text": text,
                    "metadata": {"source": str(doc_file)}
                })
            except Exception as e:
                print(f"[ERROR] Failed to process DOCX {doc_file}: {e}")
        # Combine all document texts into a single string
        document_text = "\n".join([doc["text"] for doc in documents])
        return document_text


if __name__ == "__main__":
    # Load all documents from "me" directory
    data_loader = DataLoader("me")
    document_text = data_loader.load_all_documents()
    print(document_text)
