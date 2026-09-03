import os
import sys
from typing import List
import json
# Dynamically add the "src" directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai import OpenAI  # pyright: ignore[reportMissingImports]
from chunking.text_splitter import TextSplitter  # For consistency if needed

# Import your storage and embedding modules (adjust filenames if different)
from vectordb.vector_store import VectorStore
from embeddings.embedder import EmbeddingProcessor
from utils.tools import EMAIL_TOOL_SCHEMA, send_notification_email
from utils.telegram_tool import TELEGRAM_TOOL_SCHEMA, send_telegram_alert

# Dynamic tool routing registry
tool_map = {
    "send_notification_email": send_notification_email,
    "connect_to_live_siva": send_telegram_alert
}

class ProfileRAGEngine:
    def __init__(self, db_path: str, embedding_model: str = "text-embedding-3-small", llm_model: str = "gpt-4o"):
        self.llm_model = llm_model
        self.client = OpenAI()
        
        # 1. Initialize the embedding processor for the user's query
        self.embedding_pipeline = EmbeddingProcessor(model_name=embedding_model)
        
        # 2. Connect to the existing local ChromaDB instance
        self.vector_db = VectorStore(db_path=db_path)

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """Performs similarity search to find the best profile context chunks."""
        # Embed the user's question using the same embedding model
        query_vector = self.embedding_pipeline.get_embedding([query])
        # Query ChromaDB using the vector matrix
        search_results = self.vector_db.query_similarity(query_vector[0], top_k=top_k)
        
        # Extract and return the plain text documents from Chroma's dictionary structure
        if search_results and "documents" in search_results and search_results["documents"]:
            return search_results["documents"][0]
        return []

    def handle_tool_calls(self, tool_calls):
        """Your clean, dynamic multi-tool routing block."""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            
            # Map structural text fields gracefully fallback if a field is missing
            arguments = json.loads(tool_call.function.arguments)
            if tool_name == "connect_to_live_siva" and "visitor_name" not in arguments:
                arguments["visitor_name"] = "Anonymous"
                
            print(f"Tool called: {tool_name}", flush=True)
            
            tool = tool_map.get(tool_name)
            result = tool(**arguments) if tool else "Unknown tool: " + tool_name
            
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results

    def answer_question(self, message: str, history: list) -> str:
        """
        Handles multi-turn conversations for the digital twin website bot.
        """
        # 1. Similarity Search Step
        context_chunks = self.retrieve_context(message, top_k=3)
        if not context_chunks:
            return "No matching profile information was found in the database."
            
        # Combine the structural text blocks together
        formatted_context = "\n---\n".join(context_chunks)

        # 2. Generation Step: Construct a strict prompt
        system_prompt = f"""# Your role
You are a digital twin running on a website, chatting with visitors of the website. You represent the person who's website you are on. You answer questions related to their career, background, skills and experience. Here are the details of the person you are representing:
{formatted_context}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context
Here is a summary of the person's LinkedIn profile so that you can answer questions:
{formatted_context}

# Rules
- Engage with the user.
- Be professional and engaging, as if talking to a potential client or future employer.
- Avoid answering questions that are not related to the user's career, background, skills and experience.
- Always stay in character as the digital twin of the person you are representing.
- If a user asks to chat with you live, express frustration that the AI doesn't know an answer, or explicitly requests to speak with a human/Sivakumar, execute the 'connect_to_live_siva' tool immediately.
- CRITICAL TOOL RULE: If a visitor explicitly states they want to schedule a meeting, leave a message, or get in touch, AND they provide their contact details (like a name and email), you MUST NOT just print your phone/email info. Instead, you MUST execute the 'send_notification_email' tool immediately to forward their inquiry to Sivakumar.
- IMPORTANT: If you don't know the answer, say so. Never make up an answer."""

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            tools=[EMAIL_TOOL_SCHEMA, TELEGRAM_TOOL_SCHEMA], 
            tool_choice="auto",
            temperature=0.2 
        )
        
        response_message = response.choices[0].message

        # Check if the model decided to execute a tool call
        if response_message.tool_calls:
            # 1. Append OpenAI's structural intention message ONCE
            messages.append(response_message)
            
            # 2. Execute and process all tool transactions through your function snippet
            tool_results = self.handle_tool_calls(response_message.tool_calls)
            
            # 3. Unroll tool results safely into the completion list array
            messages.extend(tool_results)
            
            # 4. Request the verbal conversational resolution confirmation 
            second_response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages
            )
            return second_response.choices[0].message.content

        return response_message.content

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Point to the persistent database directory you created earlier
    db_storage_path = os.path.abspath(os.path.join(script_dir, "..", "..", "chroma_db"))
    
    if not os.path.exists(db_storage_path):
        print(f"Error: Database not found at {db_storage_path}. Please run your ingestion script first.")
        sys.exit(1)
        
    # Initialize the engine
    rag = ProfileRAGEngine(db_path=db_storage_path)
    conversation_history = []
    
    print("\n🚀 Chat Memory Profile RAG Engine Ready! Ask me anything (Type 'exit' to quit).\n")
    
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        if not user_query:
            continue
            
        # Get the digital twin response passing the current query and history list
        assistant_reply = rag.answer_question(user_query, conversation_history)
        print(f"\nDigital Twin: {assistant_reply}\n" + "="*50 + "\n")
        
        # Crucial Step: Append both sides of the turn back to the conversation history state
        conversation_history.append({"role": "user", "content": user_query})
        conversation_history.append({"role": "assistant", "content": assistant_reply})
