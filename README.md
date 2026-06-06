# 🤖 AI Assistant Pro — Advanced RAG Chatbot

> A production-ready AI chatbot built from scratch using **LLaMA 3.3 70B** via Groq, **ChromaDB** vector search, and **Streamlit** — no LangChain, no shortcuts.

---

## ✨ Features

| Feature                    | Details                                                        |
| -------------------------- | -------------------------------------------------------------- |
| 🧠**LLM**            | LLaMA 3.3 70B via Groq API (streaming)                         |
| 📚**RAG Pipeline**   | Custom-built: chunking → embedding → vector search → prompt |
| 🗂️**Vector Store** | ChromaDB (persistent, local)                                   |
| 📄**File Support**   | PDF, TXT, MD, DOCX, CSV                                        |
| 🔐**Auth**           | Register / Login with bcrypt password hashing                  |
| 🎙️**Voice Input**  | Browser Web Speech API mic in chat bar                         |
| 💬**Chat History**   | SQLite-persisted per session                                   |
| 🎨**UI**             | Clean light-mode Claude/ChatGPT style                          |

---

## 🗂️ Project Structure

```
Advanced AI RAG Chatbot System/
│
├── app.py                  # Main Streamlit app
├── .env                    # API keys (not committed)
├── .env.example            # Env template
├── requirements.txt
├── chat_history.db         # SQLite chat + document records
│
├── auth/                   # User authentication
│   ├── __init__.py
│   ├── auth_utils.py       # Hashing, session, login/logout helpers
│   ├── database.py         # Users SQLite DB
│   ├── login.py            # Login page UI
│   └── register.py         # Register page UI
│
├── rag/                    # RAG pipeline (built from scratch)
│   ├── __init__.py
│   ├── loader.py           # File → raw text extraction
│   ├── chunker.py          # Text → overlapping chunks
│   ├── embedder.py         # Chunks → embeddings
│   ├── vector_store.py     # ChromaDB add / retrieve / delete
│   └── retriever.py        # Similarity search + context formatting
│
├── llm/                    # LLM client
│   ├── __init__.py
│   └── groq_client.py      # Groq API streaming chat
│
├── voice/                  # Voice I/O
│   ├── __init__.py
│   ├── stt.py              # Browser mic → transcript (Web Speech API)
│   └── tts.py              # Text → speech (gTTS)
│
├── utils/
│   └── helpers.py          # DB helpers, session ID, source formatting
│
├── database/
│   └── users.db            # User accounts
│
├── chroma_store/           # ChromaDB persistent storage
│
└── .streamlit/
    └── config.toml         # Force light theme
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/gapmind-ai.git
cd gapmind-ai
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🧠 How the RAG Pipeline Works

```
User uploads file
      ↓
loader.py  →  extract raw text (PDF/DOCX/TXT/CSV/MD)
      ↓
chunker.py →  split into overlapping chunks (~500 tokens)
      ↓
embedder.py → embed each chunk (sentence-transformers)
      ↓
vector_store.py → store in ChromaDB with metadata
      ↓
User asks a question
      ↓
retriever.py → embed query → cosine similarity search → top-k chunks
      ↓
groq_client.py → build prompt with context → stream LLaMA 3.3 70B response
```

No LangChain. Every step is explicit and transparent.

---

## 📦 Requirements

```
streamlit
groq
chromadb
sentence-transformers
python-dotenv
bcrypt
pypdf
python-docx
gtts
```

---

## 🔐 Auth Flow

- Passwords hashed with **bcrypt** (12 rounds)
- Sessions managed via `st.session_state`
- User records stored in **SQLite** (`database/users.db`)
- Each user gets an isolated chat session ID

---

## 🎙️ Voice Input

Uses the browser's built-in **Web Speech API** — no external API key needed. The mic button sits inside the chat input bar. Click to speak, transcript auto-fills the input. Works on Chrome and Edge.

---

## 🚀 Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as entry point
4. Add `GROQ_API_KEY` in **Secrets** settings

> Note: Voice input requires HTTPS — works on Streamlit Cloud by default.

---

## 📸 Screenshots

| Login               | Chat                         |
| ------------------- | ---------------------------- |
| Clean white auth UI | Light-mode chat with sidebar |

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io) — UI framework
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [LLaMA 3.3 70B](https://ai.meta.com/llama/) — Meta's open LLM
- [ChromaDB](https://www.trychroma.com) — Vector database
- [sentence-transformers](https://www.sbert.net) — Text embeddings
- [bcrypt](https://pypi.org/project/bcrypt/) — Password hashing
- [gTTS](https://pypi.org/project/gTTS/) — Text to speech

---

## 👨‍💻 Author

**Kokkirala Gnaneswara Anjani Prasad**
B.Tech Computer Science & Engineering | AI/ML Enthusiast

---

## 📄 License

MIT License — free to use, modify, and distribute.
