# ChatGPT Clone (FastAPI + Streamlit + Postgres/pgvector)

A simple ChatGPT-style app with:
- **FastAPI backend** (auth, sessions, chat, streaming chat)
- **Streamlit UI** that talks to the API
- **Postgres** persistence + **pgvector** embeddings column
- **Alembic** migrations
- Optional **LangServe** endpoint mounted under `/langserve`

## Project structure

- `chatgpt_clone/app/main.py`: FastAPI app (mounts routers + LangServe)
- `chatgpt_clone/streamlit_app.py`: Streamlit frontend
- `chatgpt_clone/app/database/database.py`: SQLAlchemy engine/session
- `chatgpt_clone/app/models/models.py`: `User`, `Session`, `Chat` (+ `pgvector` column)
- `chatgpt_clone/app/routers/`: `auth`, `sessions`, `chat`
- `chatgpt_clone/app/services/chat_service.py`: OpenAI Responses API + embeddings + streaming
- `chatgpt_clone/alembic.ini` + `chatgpt_clone/app/migrations/`: migrations

## Prerequisites

- **Python 3.10+**
- **PostgreSQL** with the **pgvector** extension enabled
- An **OpenAI API key**

## Environment variables

Create a `.env` file (recommended) and set:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/chatgpt_clone
SECRET_KEY=change_me
```

Notes:
- `DATABASE_URL` defaults to `postgresql+psycopg2://postgres:postgres@localhost:5432/chatgpt_clone` if not set.
- `SECRET_KEY` defaults to `mysecret` if not set (fine for local dev, not for production).

## Setup (Windows / PowerShell)

From the repo root:

```powershell
cd .\chatgpt_clone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies (this repo currently does not include a `requirements.txt`, so install the libraries used by the code):

```powershell
pip install fastapi uvicorn[standard] python-dotenv sqlalchemy psycopg2-binary alembic `
  pydantic passlib[argon2] pyjwt numpy streamlit requests `
  openai langserve langchain-openai langchain-community pgvector
```

## Database setup (Postgres + pgvector)

1) Create a database (example name used in defaults: `chatgpt_clone`).
2) Enable pgvector in that database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Run Alembic migrations

From `chatgpt_clone/`:

```powershell
alembic upgrade head
```

## Run the backend (FastAPI)

From `chatgpt_clone/`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Run the frontend (Streamlit)

In a second terminal, from `chatgpt_clone/`:

```powershell
streamlit run .\streamlit_app.py
```

The UI expects the API at `http://127.0.0.1:8000` (see `API_BASE` in `streamlit_app.py`).

## API overview

- **Auth**
  - `POST /auth/signup` → returns JWT
  - `POST /auth/login` → returns JWT
- **Sessions**
  - `POST /sessions/` → create session (requires `Authorization: Bearer <token>`)
  - `GET /sessions/all` → list sessions
  - `GET /sessions/{session_id}/chats` → chat history
- **Chat**
  - `POST /chat/message` → non-streaming reply
  - `POST /chat/stream` → token streaming (`text/plain`)

## LangServe (optional)

The FastAPI app mounts LangServe under `/langserve` (see `app/main.py`), with a route at:
- `/langserve/chatbot`

## Troubleshooting

- **401 “Invalid Authorization header”**: Make sure you send `Authorization: Bearer <token>`.
- **DB errors / missing `vector` type**: Ensure pgvector is installed and `CREATE EXTENSION vector;` was run.
- **OpenAI errors**: Confirm `OPENAI_API_KEY` is set in your environment or `.env`.

