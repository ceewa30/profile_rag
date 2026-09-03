import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # pyright: ignore[reportMissingImports]
import requests  # pyright: ignore[reportMissingModuleSource]

# Dynamically add the "src" directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
load_dotenv(override=True)

# Import your custom modules
from src.retrieval.retriever import ProfileRAGEngine

app = FastAPI(title="Digital Twin Live RAG Gateway")

# Enable CORS so your website frontend can securely communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your specific website domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MY_CHAT_ID = os.getenv("TELEGRAM_MY_CHAT_ID")

# Initialize your custom RAG Engine
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_STORAGE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "chroma_db"))
rag_engine = ProfileRAGEngine(db_path=DB_STORAGE_PATH)

# State Management Connections Cache
# Tracks active website users: { session_id: { "websocket": WebSocket, "history": list, "live_mode": bool } }
active_connections = {}
# Maps outbound Telegram message IDs back to website session IDs: { telegram_msg_id: session_id }
telegram_message_map = {}


@app.on_event("startup")
async def startup_event():
    """Verify core credentials on app launch."""
    if not BOT_TOKEN or not MY_CHAT_ID:
        print("\n⚠️ WARNING: Telegram integration credentials missing in .env configuration!\n")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Siva's Digital Twin Gateway is fully active. Use WebSocket endpoints to chat."}
    
@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Manages the long-lived, real-time browser session connection for website visitors."""
    await websocket.accept()
    
    # Register the session tracking dictionaries
    active_connections[session_id] = {
        "websocket": websocket,
        "history": [],
        "live_mode": False
    }
    
    print(f"🔌 New visitor connected. Session initialized: {session_id}")
    
    try:
        while True:
            # Listen for incoming text payloads from the website widget
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            user_msg = data.get("text", "").strip()
            
            if not user_msg:
                continue
                
            session = active_connections[session_id]
            
            # 1. LIVE HUMAN HANDOVER MODE: Forward message directly to Telegram, skipping the LLM
            if session["live_mode"]:
                endpoint = f"https://telegram.org{BOT_TOKEN}/sendMessage"
                res = requests.post(endpoint, json={
                    "chat_id": MY_CHAT_ID,
                    "text": f"👤 *Live Visitor ({session_id}):*\n{user_msg}",
                    "parse_mode": "Markdown"
                })
                
                if res.status_code == 200:
                    msg_id = res.json().get("result", {}).get("message_id")
                    # Bind this specific message ID thread to the current session user
                    telegram_message_map[str(msg_id)] = session_id
                continue
            
            # 2. AUTOMATED AI TWIN MODE: Process message through local RAG Engine
            # Pass user text query along with the session's isolated conversational history tracker
            ai_reply = rag_engine.answer_question(user_msg, session["history"])
            
            # Detect if the model chose to invoke the 'connect_to_live_siva' tool in the background
            # If your retriever module indicates a handover occurred, toggle live_mode status flags
            if "successfully notified via Telegram" in ai_reply or "Switching session control" in ai_reply:
                session["live_mode"] = True
                # Seed a fallback placeholder anchor message inside Telegram so you can reply to it
                endpoint = f"https://telegram.org{BOT_TOKEN}/sendMessage"
                res = requests.post(endpoint, json={
                    "chat_id": MY_CHAT_ID,
                    "text": f"🚨 *System initiated conversation handover.*\n*Visitor Session:* `{session_id}`\n*Opening question:* {user_msg}",
                    "parse_mode": "Markdown"
                })
                if res.status_code == 200:
                    msg_id = res.json().get("result", {}).get("message_id")
                    telegram_message_map[str(msg_id)] = session_id

            # Cache the ongoing conversation back to this visitor's history block
            session["history"].append({"role": "user", "content": user_msg})
            session["history"].append({"role": "assistant", "content": ai_reply})
            
            # Push the generated response string back to the browser interface immediately
            await websocket.send_text(json.dumps({
                "sender": "Digital Twin",
                "text": ai_reply
            }))
            
    except WebSocketDisconnect:
        print(f"❌ Session disconnected: {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Listens for updates hitting your server from Telegram.
    Fires instantly whenever you use 'Reply to Message' inside your mobile app.
    """
    payload = await request.json()
    
    # Safely isolate reply threading components
    if "message" in payload and "reply_to_message" in payload["message"]:
        reply_to_id = str(payload["message"]["reply_to_message"]["message_id"])
        my_reply_text = payload["message"].get("text", "").strip()
        
        # Verify if the message ID corresponds to an active website user socket session
        if reply_to_id in telegram_message_map:
            target_session_id = telegram_message_map[reply_to_id]
            
            if target_session_id in active_connections:
                visitor_ws = active_connections[target_session_id]["websocket"]
                
                # Instantly inject your phone string to their web front-end
                await visitor_ws.send_text(json.dumps({
                    "sender": "Sivakumar (Live)",
                    "text": my_reply_text
                }))
                return {"status": "routed_to_visitor"}
                
    return {"status": "ignored"}
