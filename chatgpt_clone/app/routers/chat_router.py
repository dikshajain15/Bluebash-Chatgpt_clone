# app/routers/chat_router.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.database.database import get_db
from app.utils.security import decode_access_token
from app.models.models import Session as SessionModel
from app.schemas.schemas import ChatCreateRequest, ChatResponse

from app.services.chat_service import (
    save_user_message,
    get_similar_chats,
    save_assistant_reply,
    generate_ai_reply,
    generate_ai_reply_stream
)

router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------
# Extract current user from Authorization header
# ---------------------------------------------------
def get_current_user_from_header(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ---------------------------------------------------
# NORMAL (NON-STREAMING) CHAT COMPLETION
# ---------------------------------------------------
@router.post("/message", response_model=ChatResponse)
def send_message(
    req: ChatCreateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    # 1. Decode JWT
    payload = get_current_user_from_header(authorization, db)

    # 2. Validate session
    sess = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    if not sess or sess.user_id != payload.get("user_id"):
        raise HTTPException(status_code=400, detail="Invalid session")

    # 3. Save user message
    save_user_message(db, req.session_id, req.message)

    # 4. Retrieve vector-context
    context_chunks = get_similar_chats(db, req.message, top_k=6)

    # 5. Generate LLM reply
    assistant_text = generate_ai_reply(req.message, context_chunks)

    # 6. Save assistant reply
    saved = save_assistant_reply(db, req.session_id, assistant_text)

    # 7. Return to UI
    return ChatResponse(
        id=saved.id,
        role="assistant",
        content=saved.content
    )


# ---------------------------------------------------
# STREAMING CHAT (TOKENS LIKE CHATGPT)
# ---------------------------------------------------
@router.post("/stream")
def send_message_stream(
    req: ChatCreateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    # 1. Decode JWT
    payload = get_current_user_from_header(authorization, db)

    # 2. Validate user session
    sess = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    if not sess or sess.user_id != payload.get("user_id"):
        raise HTTPException(status_code=400, detail="Invalid session")

    # 3. Save user message
    save_user_message(db, req.session_id, req.message)

    # 4. Get relevant context
    context_chunks = get_similar_chats(db, req.message, top_k=6)

    # 5. Streaming generator
    def token_generator():
        full_text = ""
        for token in generate_ai_reply_stream(req.message, context_chunks):
            full_text += token
            yield token  # send token to client

        # Save assistant reply after full generation
        save_assistant_reply(db, req.session_id, full_text)

    return StreamingResponse(token_generator(), media_type="text/plain")
