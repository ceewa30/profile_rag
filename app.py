from src.RAGsearch import RAGSearch


if __name__ == "__main__":
    # RAG Search
    rag_search = RAGSearch()

    query_text = "do you done any certification."
    summary = rag_search.search_and_summarize(query_text=query_text, n_results=2)
    print("Summary:")
    print(summary)
