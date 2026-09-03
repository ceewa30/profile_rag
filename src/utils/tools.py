import os
import json
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any

# 1. The OpenAI Function Call Schema Definition
EMAIL_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "send_notification_email",
        "description": "Sends a notification email to Siva when a website visitor wants to leave a message, schedule a meeting, or get in touch.",
        "parameters": {
            "type": "object",
            "properties": {
                "visitor_name": {
                    "type": "string", 
                    "description": "The name of the visitor."
                },
                "visitor_email": {
                    "type": "string", 
                    "description": "The contact email address provided by the visitor."
                },
                "message_content": {
                    "type": "string", 
                    "description": "The full core message or context left by the visitor."
                }
            },
            "required": ["visitor_name", "visitor_email", "message_content"]
        }
    }
}

# 2. The Core Execution Engine
def send_notification_email(visitor_name: str, visitor_email: str, message_content: str) -> str:
    """
    Sends an alert email via SMTP.
    Requires SMTP_SENDER_EMAIL, SMTP_RECEIVER_EMAIL, and SMTP_APP_PASSWORD in your .env file.
    """
    sender_email = os.getenv("SMTP_SENDER_EMAIL")
    receiver_email = os.getenv("SMTP_RECEIVER_EMAIL")
    smtp_password = os.getenv("SMTP_APP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "://gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    # Fail-safe check for missing environment configs
    if not all([sender_email, receiver_email, smtp_password]):
        return "Failed to send email: SMTP credentials or receiver endpoints are missing in .env config."

    subject = f"💼 Digital Twin Alert: New Message from {visitor_name}"
    body = (
        f"You received a new inquiry via your Digital Twin website agent.\n\n"
        f"----------------------------------------\n"
        f"Visitor Name: {visitor_name}\n"
        f"Visitor Email: {visitor_email}\n"
        f"----------------------------------------\n\n"
        f"Message:\n{message_content}"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())
        return "Email notification sent successfully to Siva!"
    except Exception as e:
        return f"Failed to deliver email. Error details: {str(e)}"


if __name__ == "__main__":
    from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
    # Explicitly pull env variables up for this quick test
    load_dotenv(override=True)
    
    print("Testing email configuration parameters...")
    print(f"Sender: {os.getenv('SMTP_SENDER_EMAIL')}")
    print(f"Receiver: {os.getenv('SMTP_RECEIVER_EMAIL')}")
    print(f"Has Password?: {'Yes' if os.getenv('SMTP_APP_PASSWORD') else 'No'}")
    
    # Run a manual check
    test_status = send_notification_email(
        visitor_name="John Doe Test",
        visitor_email="john.doe@example.com",
        message_content="This is a strict local debugging script test."
    )
    print(f"\nResult: {test_status}")