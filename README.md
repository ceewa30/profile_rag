# Profile RAG Digital Twin

A lightweight, zero-dependency, production-ready Retrieval-Augmented Generation (RAG) application designed to act as an interactive AI digital twin for your personal or portfolio website.

The system runs a FastAPI backend handling concurrent website visitors via persistent WebSockets. It answers professional questions about your career, background, and skills using a local vector database (ChromaDB). When human escalation is needed, it features custom Parallel Tool Calling to instantly dispatch notification emails and establish a live communication bridge directly to your phone via Telegram Webhooks.

# 🏗️ Production Architecture

┌────────────────────────┐      ┌────────────────────┐      ┌────────────────────────┐
│    1. DATA INGESTION   │ ───► │ 2. LOCAL VECTOR DB │ ◄─── │  3. FASTAPI GATEWAY    │
│  DataLoader & Splitter │      │     ChromaDB       │      │  WebSockets & Webhooks │
└────────────────────────┘      └────────────────────┘      └───────────▲────────────┘
                                                                        │
                                                            ┌───────────▼────────────┐
                                                            │  4. CORE INTERACTION   │
                                                            │    ProfileRAGEngine    │
                                                            └───────────┬────────────┘
                                                                        │ (Parallel Tools)
                                                     ┌──────────────────┴──────────────────┐
                                                     ▼                                     ▼
                                            ┌──────────────────┐                  ┌──────────────────┐
                                            │    Email Tool    │                  │  Telegram Tool   │
                                            │   (SMTP Relay)   │                  │ (Live Handover)  │
                                            └──────────────────┘                  └──────────────────┘


# ✨ Features

#### Framework-Free Ingestion Pipeline: 

Custom, recursive string splitting algorithms built entirely in pure Python—no bulky third-party abstraction overhead.

#### Batched Matrix Embeddings: 

Integrated with OpenAI's optimized text-embedding-3-small vector generation, processing file fragments in structural batches to minimize latency and API costs.

#### Isolated Session State Tracking: 

Manages unique client-side session contexts, maintaining individual message thread memory histories completely independent of concurrent traffic.

#### Parallel Tool Calling & Routing Engine: 

Multi-agent processing block handles simultaneous tool calls seamlessly when a user triggers background tasks (e.g., asking to leave a message and speak with you live).

#### Bi-Directional Mobile Bridge: 

Forwards live website chats directly to your personal Telegram client app. Replying directly to the notification on your phone pushes the text back to the browser interface instantly.

# 📁 Repository Structuretext

├── chroma_db/               # Local folder-backed persistent vector index database
├── me/                      # Raw text sources (Resumes, cover letters, Markdown logs)
├── tools/
│   ├── email_tool.py        # Independent SMTP module and OpenAI function definitions
│   └── telegram_tool.py     # Independent Telegram integration module and API handlers
├── embeddings/
│   └── embedder.py          # Array batch matrix vector rendering implementation
├── vectordb/
│   └── vector_store.py      # Custom ChromaDB instance client initialization mapping
├── chunking/
│   └── text_splitter.py     # Hierarchical structural paragraph text slicing mechanics
├── retrieval/
│   └── retriever.py         # Main ProfileRAGEngine client framework layer
├── main.py                  # Core FastAPI multi-user connection endpoint router gateway
├── index.html               # Frontend UI floating bubble widget sandbox interface
├── .env                     # Private application credential configurations (Git ignored)
├── Dockerfile               # Production Multi-Stage minimal runtime system blueprint
└── requirements.txt         # Pinned module dependencies block file

# 🚀 Quick Start Guide

## 1. Prerequisites

Ensure you have Python 3.12 installed. This project uses the ultra-fast uv workflow tool for virtual environment tracking and package resolution management.

pip install uv

## 2. Installation & Dependency Sync

Clone your repository, navigate to the folder, initialize a clean isolated space, and pull down the library packages:

uv venv
source .venv/bin/activate
uv pip install fastapi uvicorn openai chromadb python-dotenv requests

## 3. Setup Your Environment Credentials

#### Create a file named .env right in your root directory and map out your system keys:

env

#### "Core OpenAI Model"

OPENAI_API_KEY="sk-proj-..."

#### Email Configurations (Gmail SMTP Example)

SMTP_SERVER="://gmail.com"
SMTP_PORT=587
SMTP_SENDER_EMAIL="your_system_email@gmail.com"
SMTP_RECEIVER_EMAIL="your_personal_inbox@gmail.com"
SMTP_APP_PASSWORD="xxxx xxxx xxxx xxxx" # 16-character Google App Password

#### Mobile Telegram Handover Integration

TELEGRAM_BOT_TOKEN="xxxxxxxxxxxxxxxx"
TELEGRAM_MY_CHAT_ID="xxxxxxxxxxxxxxxx"

## 4. Seed the Vector Database Index

Place your profile documents (PDFs, TXT, DOCX, or Markdown files) inside the /me directory, then execute your chunking and ingestion module to create the embedding indexes locally:

uv run python chunking/text_splitter.py

## 5. Launch the Server Gateway

Fire up your live production FastAPI instance server, setting explicit exclusion commands so background package file indexing doesn't disrupt auto-reloads:

uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude ".venv"

Open index.html directly in any web browser to connect to your live backend over localized loop sockets (ws://127.0.0.1:8000) and test out your digital twin interface sandbox!

# 🐳 Docker Production Deployment

This project uses a standard, slim Multi-Stage Dockerfile tracking footprint environments to minimize cloud container sizing and protect your secret key dependencies.

Generate your production-pinned requirements block, compile your lightweight image, and trigger local verification runs using the commands below:

#### Freeze your current locked dependencies

uv pip freeze > requirements.txt

#### Compile the production container image

docker build -t profile-rag-twin:latest .

#### Launch locally by safely piping in your active env strings

docker run -d -p 8000:8000 --env-file .env --name siva-twin profile-rag-twin:latest


# 🔒 Security & Best Practices

### Repository Ignored Configs: 

Your custom .env configurations are explicitly blocked via .gitignore to prevent secret authorization keys or secure email passwords from accidentally hitting public git remotes.

### Production Variable Overrides: 

When deploying onto an active cloud engine (like Render, Railway, or AWS), do not bake credentials into the build. Map your connection tokens securely using your provider's native Environment Variable Dashboard Configuration panels.
