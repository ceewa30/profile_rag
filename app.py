from src.RAGsearch import RAGSearch
import streamlit as st



if __name__ == "__main__":
    # RAG search
    rag_search = RAGSearch()

    st.title("RAG Chatbot about Yourself")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Waiting for your query..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display chatbot response (replace with your actual chatbot logic)
        with st.chat_message("assistant"):
            summary = rag_search.search_and_summarize(query_text=prompt, n_results=2)
            response = summary # Placeholder response
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
