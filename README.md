##### Profile Retrieval-Augmented Generation

Profile Retrieval-Augmented Generation (Profile RAG) using PDFs, TXT, and DOCX files involves a sophisticated workflow designed to extract, interpret, and leverage user-specific or entity-specific information scattered across various unstructured document formats. The ultimate goal is to enable an AI system to answer complex, precise questions about the profile data by grounding its responses in the provided files.

The process is typically broken down into several key stages,

1. Data Ingestion & Parsing: The system first processes the raw files. This is a critical step because each format—PDFs (complex layouts), plain TXT files (simple text), and DOCX files (structured XML)—requires specialized parsers to reliably extract clean, continuous text while maintaining structural integrity.

2. Chunking & Embedding: The vast amount of extracted text is then segmented into smaller, contextually relevant passages, known as "chunks." These chunks are then transformed into high-dimensional numerical representations called vectors or embeddings using a specialized embedding model. These embeddings capture the semantic meaning of the text.

3. Storage in ChromaDB: The vector embeddings, along with associated metadata (like source document name, page number, or original text snippet), are stored and indexed within a vector database, such as ChromaDB. ChromaDB is an open-source, lightweight database optimized for vector similarity search, allowing for rapid retrieval of relevant information later in the process.

4. Retrieval: When a user poses a question about the profile (e.g., "What was the specific project timeline mentioned in the Word document for ceewa?"), the user's query is also embedded into a vector. The RAG system queries the ChromaDB instance to find the top \(k\) most semantically similar text chunks to that query.

5. Augmentation & Generation: The retrieved chunks are passed to a Large Language Model (LLM) as context within the prompt. This augmentation prevents the LLM from hallucinating or relying solely on its internal training data. The LLM synthesizes the provided context into a precise, accurate, and source-grounded answer regarding the profile data. This ensures the answer is verifiable against the original PDFs, TXT, and DOCX files stored in the ChromaDB.

###### Step to excute the project ############

Step 1. Run requirement.txt

Step 2. Create a folder name me in root directory

Step 3. Place the profile pdf, txt, docx extension document in me folder
