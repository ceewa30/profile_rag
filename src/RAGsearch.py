import os
import json as json_module
import requests
from dotenv import load_dotenv
from streamlit import json
from openai import OpenAI
from src.data_loader import DataLoader
from src.chromastore import ChromaStore

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The email address of this user"
                    },
                    "name": {
                        "type": "string",
                        "description": "The user's name, if they provided it"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any additional information about the conversation to provide context"
                    }
                },
                "required": ["email"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Always use this tool to record any question that couldn't be answered because the answer was unknown",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The exact question that couldn't be answered"
                    }
                },
                "required": ["question"],
                "additionalProperties": False
            }
        }
    }
]

class RAGSearch:
    def __init__(self, chroma_store_path: str = "chroma_store", embedding_model: str = "text-embedding-ada-002", llm_model: str = "gpt-4"):
        self.name = "Sivakumar Santhalingam"
        self.chroma_store = ChromaStore(persist_directory=chroma_store_path, embedding_function=embedding_model)

        current_directory = os.getcwd()
        data_loader = DataLoader(f"{current_directory}/me")
        document = data_loader.load_all_documents()
        self.build_store(document)
        self.load_store()
        self.llm_model = llm_model

    def build_store(self, documents):
        print(f"DEBUG: Processing document: {documents}")
        self.chroma_store.build_from_documents(documents)

    def load_store(self):
        self.chroma_store.load()

    # FIX: Renamed 'json' parameter to avoid overriding the json module global namespace
    def handle_tool_call(self, tool_calls, json_helper=None):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json_module.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)

            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}

            results.append({
                "role": "tool",
                "content": json_module.dumps(result), # FIX: Safely using json_module
                "tool_call_id": tool_call.id
            })
        return results

    def system_prompt(self):
        system_prompt = (
            f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
            f"particularly questions related to {self.name}'s career, background, skills and experience. "
            f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            f"You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
            f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
            f"If you don't know the answer to any question, use your record_unknown_question tool to record the question that you "
            f"couldn't answer, even if it's about something trivial or unrelated to career. "
            f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "
            f"With this context, please chat with the user, always staying in character as {self.name}."
        )
        return system_prompt

    def search_and_summarize(self, query_text: str, n_results: int = 2, history: list = None) -> str:
        if history is None:
            history = []

        results = self.chroma_store.query(query_text=query_text, n_results=n_results)

        # Pull text accurately depending on Chroma store's returns format
        # Check standard chroma output or structured document content fallback
        if results and results.get('documents') and len(results['documents'][0]):
            texts = [doc for doc in results['documents'][0] if doc]
        elif results and results.get('metadatas') and len(results['metadatas'][0]):
            texts = [meta.get('text', '') for meta in results['metadatas'][0] if meta]
        else:
            texts = ['No relevant information found in the database.']

        combined_text = "\n\n".join(texts)
        prompt = f"The user asked: '{query_text}'. Here is the background info found:\n\n{combined_text}"

        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": prompt}]

        done = False
        summary = ""

        while not done:
            # FIX: Included tools and tool_choice structure safely for looping
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                n=1,
                max_completion_tokens=400, # Increased slightly to ensure long content summaries fit
                stop=None,
            )

            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                message = choice.message
                tool_calls = message.tool_calls
                tool_results = self.handle_tool_call(tool_calls)

                # Update history to continue loop with context
                messages.append(message)
                messages.extend(tool_results)
            else:
                done = True
                if choice.message.content:
                    summary = choice.message.content.strip()

        return summary

if __name__ == "__main__":
    rag_search = RAGSearch()
    query_text = "Tell me about yourself."
    summary = rag_search.search_and_summarize(query_text=query_text, n_results=2)
    print("Summary:")
    print(summary)
