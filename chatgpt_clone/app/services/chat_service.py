# app/services/chat_service.py

from sqlalchemy.orm import Session
from app.models.models import Chat
import numpy as np
from openai import OpenAI
import os

# Initialize OpenAI client (NEW SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL  = "gpt-4o-mini"


# ----------------------------------------------------
# Generate Embeddings
# ----------------------------------------------------
def get_embedding(text: str):
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return resp.data[0].embedding


# ----------------------------------------------------
# Save user message
# ----------------------------------------------------
def save_user_message(db: Session, session_id: int, message: str):
    emb = get_embedding(message)
    chat = Chat(session_id=session_id, role="user", content=message, embedding=emb)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


# ----------------------------------------------------
# Save assistant reply
# ----------------------------------------------------
def save_assistant_reply(db: Session, session_id: int, content: str):
    emb = get_embedding(content)
    chat = Chat(session_id=session_id, role="assistant", content=content, embedding=emb)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


# ----------------------------------------------------
# Retrieve similar chats (Context Retrieval)
# ----------------------------------------------------
def get_similar_chats(db: Session, text: str, top_k: int = 5):
    new_emb = get_embedding(text)

    rows = db.query(Chat).filter(Chat.embedding != None).all()
    if not rows:
        return []

    embeddings = np.array([np.array(r.embedding, dtype=float) for r in rows])
    ids       = [r.id for r in rows]
    contents  = [r.content for r in rows]
    roles     = [r.role for r in rows]

    new = np.array(new_emb, dtype=float)

    sims = embeddings.dot(new) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(new)
    )

    top_idx = np.argsort(-sims)[:top_k]

    results = []
    for i in top_idx:
        results.append({
            "id": ids[i],
            "content": contents[i],
            "role": roles[i],
            "score": float(sims[i])
        })

    return results


# ----------------------------------------------------
# NON-STREAMING RESPONSE (NEW SDK)
# ----------------------------------------------------
def generate_ai_reply(message: str, context_chunks: list):
    """
    NEW OPENAI SDK — DOES NOT SUPPORT messages=[]
    We must send full text in a single `input` field.
    """

    system_prompt = "You are a helpful assistant inside a ChatGPT clone.\n"

    # Build one big text prompt
    full_input = system_prompt + "\n"

    for ctx in context_chunks:
        full_input += f"{ctx['role']}: {ctx['content']}\n"

    full_input += f"user: {message}\nassistant:"

    # NEW SDK CALL (correct)
    resp = client.responses.create(
        model=CHAT_MODEL,
        input=full_input
    )

    return resp.output_text


# ----------------------------------------------------
# STREAMING RESPONSE (token-by-token)
# ----------------------------------------------------
def generate_ai_reply_stream(message: str, context_chunks: list):
    """
    NEW SDK streaming also uses `input=`, not messages=[]
    """

    system_prompt = "You are a helpful assistant inside a ChatGPT clone.\n"

    full_input = system_prompt + "\n"

    for ctx in context_chunks:
        full_input += f"{ctx['role']}: {ctx['content']}\n"

    full_input += f"user: {message}\nassistant:"

    stream = client.responses.create(
        model=CHAT_MODEL,
        input=full_input,
        stream=True
    )

    final_text = ""

    for chunk in stream:
        if hasattr(chunk, "output_text") and chunk.output_text:
            token = chunk.output_text
            final_text += token
            yield token

    return final_text
