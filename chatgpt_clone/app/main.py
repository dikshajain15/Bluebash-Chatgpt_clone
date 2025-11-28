# app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

# Routers
from app.routers.auth import router as auth_router
from app.routers.session_router import router as session_router
from app.routers.chat_router import router as chat_router

app = FastAPI(title="ChatGPT Clone")

# Register routes
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(chat_router)
from app.langserve_server import app as langserve_app
app.mount("/langserve", langserve_app)

