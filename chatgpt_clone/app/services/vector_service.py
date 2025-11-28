import os
from sqlalchemy.orm import Session
from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings

from app.models.models import Chat

# Embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def get_connection_string():
    DB_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/chatgpt_clone"
    )
    return DB_URL.replace("+psycopg2", "")  # pgvector needs plain postgresql://


def load_vector_store():
    return PGVector(
        connection_string=get_connection_string(),
        embedding_function=embeddings,
        collection_name="chat_history_vectors"
    )


def sync_db_to_vectorstore(db: Session):
    """
    Load all chats from DB → push into vector store
    """
    store = load_vector_store()

    rows = db.query(Chat).all()
    documents = []
    metadatas = []
    ids = []

    for c in rows:
        if c.embedding is None:
            continue

        documents.append(c.content)
        metadatas.append({"role": c.role, "session_id": c.session_id})
        ids.append(str(c.id))

    if documents:
        store.add_texts(documents=documents, metadatas=metadatas, ids=ids)

    return store


def similarity_search(db: Session, query: str, k: int = 5):
    store = sync_db_to_vectorstore(db)
    results = store.similarity_search(query, k=k)
    return results
