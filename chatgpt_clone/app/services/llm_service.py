from langchain_openai import ChatOpenAI
from app.services.vector_service import similarity_search

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)


def call_llm(user_message: str, db):
    """
    Run vector search + LLM response
    """

    # 1. Retrieve similar chats
    results = similarity_search(db, user_message, k=5)

    context = "\n".join([f"{r.metadata['role']}: {r.page_content}" for r in results])

    prompt = f"""
You are a helpful assistant.
Here is the conversation context:

{context}

User: {user_message}
Assistant:
"""

    response = llm.invoke(prompt)
    return response.content
