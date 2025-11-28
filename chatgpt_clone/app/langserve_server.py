from fastapi import FastAPI
from langserve import add_routes
from langchain_openai import ChatOpenAI
from app.services.llm_service import call_llm

app = FastAPI(title="ChatGPT Clone LangServe API")

# Simple LLM wrapper
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5
)

# LangServe route
add_routes(app, llm, path="/chatbot")
