import os
import sys

# Dynamically add the "src" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.data_loader import DataLoader

class TextSplitter:
    """A lightweight, zero-dependency recursive text splitter designed for profile data."""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Prioritize paragraphs, then line breaks/bullets, then words
        self._separators = ["\n\n", "\n", " "]

    def split_text(self, text: str) -> list[str]:
        """Public method to split a raw string into structured chunks."""
        if not text:
            return []
        return self._split_recurse(text.strip(), self._separators)

    def _split_recurse(self, current_text: str, seps: list[str]) -> list[str]:
        """Internal recursive engine that splits text along structural boundaries."""
        # Base case: If text already fits within the limit, return it as a single chunk
        if len(current_text) <= self.chunk_size:
            return [current_text]
        
        # If we ran out of structural separators, perform a raw slice
        if not seps:
            return self._hard_slice(current_text)
        
        current_sep = seps[0]
        remaining_seps = seps[1:]
        
        # Split text by the current highest-priority separator
        parts = current_text.split(current_sep)
        sub_chunks = []
        current_buffer = ""
        
        for part in parts:
            # If an individual segment is still too large, force it to split recursively
            if len(part) > self.chunk_size:
                if current_buffer:
                    sub_chunks.append(current_buffer)
                    current_buffer = ""
                sub_chunks.extend(self._split_recurse(part, remaining_seps))
                
            # If the part fits into our current running chunk, append it
            elif len(current_buffer) + len(part) + len(current_sep) <= self.chunk_size:
                current_buffer = f"{current_buffer}{current_sep}{part}" if current_buffer else part
                
            # If adding the part overflows the limit, save the buffer and start a new one
            else:
                if current_buffer:
                    sub_chunks.append(current_buffer)
                
                # Apply overlap lookback context from the end of the previous buffer
                lookback = current_buffer[-self.chunk_overlap:] if len(current_buffer) >= self.chunk_overlap else current_buffer
                current_buffer = f"{lookback}{current_sep}{part}" if lookback else part
                
        # Catch any trailing text left in the buffer
        if current_buffer:
            sub_chunks.append(current_buffer)
            
        return sub_chunks

    def _hard_slice(self, text: str) -> list[str]:
        """Fallback method to slice text by exact character count if no separators fit."""
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks


if __name__ == "__main__":
    import os
    
    # 1. Initialize your splitter with customized boundaries
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

    # 2. Resolve absolute paths dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Inside /src/chunking/
    
    # FIX: Go up TWO levels to reach the root /profile_rag/, then down into /me/
    target_path = os.path.abspath(os.path.join(script_dir, "..", "..", "me"))

    # 3. Pass the resolved absolute path to your loader
    data_loader = DataLoader(target_path)
    documents = data_loader.load_all_documents()
    all_profile_chunks = []
    
    # If load_all_documents returns a list of strings or doc objects
    if isinstance(documents, list):
        for doc in documents:
            # Extract raw string text if it's an object, or use directly if it's already a string
            raw_text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            all_profile_chunks.extend(splitter.split_text(raw_text))
            
    # Fallback if it returns a single monolithic string
    elif isinstance(documents, str):
        all_profile_chunks = splitter.split_text(documents)

    # 5. Inspect and verify the final chunks
    print(f"Successfully generated {len(all_profile_chunks)} chunks.")
    for idx, chunk in enumerate(all_profile_chunks):
        print(f"\n--- Chunk {idx + 1} ---")
        print(chunk)