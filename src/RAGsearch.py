import os
from dotenv import load_dotenv
from src.chromastore import ChromaStore
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv(override=True)

class RAGSearch:
    def __init__(self, chroma_store_path: str = "chroma_store", embedding_model: str = "text-embedding-ada-002", llm_model: str = "gpt-4.1-nano"):
        self.name = "Sivakumar Santhalingam" # Your name here

        self.chroma_store = ChromaStore(persist_directory=chroma_store_path, embedding_function=embedding_model)

        # Load or build the Chroma store
        data_loader = DataLoader("/Users/sivakumars/Documents/Agentic_AI/me")
        document = data_loader.load_all_documents()
        self.build_store(document)
        self.load_store()
        self.llm_model = llm_model

    def build_store(self, documents):
        self.chroma_store.build_from_documents(documents)

    def load_store(self):
        self.chroma_store.load()

    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
        particularly questions related to {self.name}'s career, background, skills and experience. \
        Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
        You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
        Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
        If you don't know the answer to any question, use your record_unknown_question tool to record the question that you  \
        couldn't answer, even if it's about something trivial or unrelated to career. \
        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt

    def search_and_summarize(self, query_text: str, n_results: int = 2) -> str:
        results = self.chroma_store.query(query_text=query_text, n_results=n_results)
        texts = [r[0]['text'] for r in results['metadatas']]
        combined_text = "\n\n".join(texts)
        prompt = f"Summarize the following information in relation to the query '{query_text}':\n\n{combined_text}"
        response = client.chat.completions.create(model=self.llm_model,
        messages=[
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.7)
        summary = response.choices[0].message.content.strip()
        return summary



if __name__ == "__main__":
    rag_search = RAGSearch()
    query_text = "Tell me about yourself."
    summary = rag_search.search_and_summarize(query_text=query_text, n_results=2)
    print("Summary:")
    print(summary)
