import os 
import requests   # pyright: ignore[reportMissingModuleSource]
from typing import Dict, Any 

# 1. Function Call Schema for OpenAI 
TELEGRAM_TOOL_SCHEMA = { 
    "type": "function", 
    "function": { 
        "name": "connect_to_live_siva", 
        "description": "Alerts Sivakumar via Telegram that a website visitor wants to transition to a live chat conversation because the AI does not know the answer or they requested a human.", 
        "parameters": { 
            "type": "object", 
            "properties": { 
                "visitor_name": {"type": "string", "description": "The name of the website visitor if known, otherwise 'Anonymous'."}, 
                "last_message": {"type": "string", "description": "The current question or context driving the human request."} 
            }, 
            "required": ["visitor_name", "last_message"] 
        } 
    } 
} 

# 2. Main Alert Transmission Engine 
def send_telegram_alert(visitor_name: str, last_message: str) -> str: 
    """Sends a formatted notification payload directly to your personal Telegram app.""" 
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN") 
    chat_id = os.getenv("TELEGRAM_MY_CHAT_ID") 
    
    if not bot_token or not chat_id: 
        return "Failed to alert via Telegram: Missing integration credentials in configuration file." 
        
    text_payload = ( 
        f"🚨 *Digital Twin Handover Alert*\n" 
        f"👤 *Visitor:* {visitor_name}\n" 
        f"💬 *Context:* {last_message}\n\n" 
        f"⚠️ Switching session control to Live Mode." 
    ) 
    
    # FIX: Use api.telegram.org and prefix the token with the word 'bot'
    endpoint_url = f"https://api.telegram.org/bot{bot_token}/sendMessage" 
    
    payload = { 
        "chat_id": chat_id, 
        "text": text_payload, 
        "parse_mode": "Markdown" 
    } 
    
    try: 
        response = requests.post(endpoint_url, json=payload, timeout=10) 
        if response.status_code == 200: 
            return "Sivakumar has been successfully notified via Telegram. He will respond shortly if available." 
        return f"Telegram API rejected message with status code: {response.status_code}. Response: {response.text}" 
    except Exception as e: 
        return f"Failed to connect to Telegram network services. Details: {str(e)}" 

if __name__ == "__main__": 
    # from dotenv import load_dotenv 
    # load_dotenv(override=True) 
    
    # print("--- Telegram Integration Diagnostic ---") 
    # print(f"Bot Token Loaded: {'Yes' if os.getenv('TELEGRAM_BOT_TOKEN') else 'No'}") 
    # print(f"Chat ID Loaded: {os.getenv('TELEGRAM_MY_CHAT_ID')}") 
    
    # # FIX: Use api.telegram.org/bot for the testing diagnostic check as well
    # url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/getMe" 
    
    # try: 
    #     res = requests.get(url) 
    #     print(f"Bot Connection Test: Status {res.status_code} - Details: {res.text}") 
    # except Exception as e: 
    #     print(f"Network Connection Failed: {str(e)}")
    
    from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
    load_dotenv(override=True)
    
    print("Sending live test alert to your phone...")
    status_msg = send_telegram_alert(
        visitor_name="John Doe Developer",
        last_message="I would like to verify that the RAG pipeline can buzz Sivakumar's phone in real time."
    )
    print(f"Transmission Result: {status_msg}")
