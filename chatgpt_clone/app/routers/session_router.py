# app/routers/session_router.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.security import decode_access_token
from app.models.models import Session as SessionModel, Chat
from app.schemas.schemas import SessionCreateResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


# ---------- Get current user ----------
def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ---------- CREATE NEW SESSION ----------
@router.post("/", response_model=SessionCreateResponse)
def create_session(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    payload = get_current_user(authorization)

    new_session = SessionModel(user_id=payload["user_id"])
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return SessionCreateResponse(id=new_session.id)


# ---------- GET ALL SESSIONS ----------
@router.get("/all")
def get_all_sessions(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    payload = get_current_user(authorization)

    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == payload["user_id"])
        .order_by(SessionModel.id.desc())
        .all()
    )

    return [{"id": s.id} for s in sessions]


# ---------- GET CHAT HISTORY FOR A SESSION ----------
@router.get("/{session_id}/chats")
def get_session_chats(
    session_id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    payload = get_current_user(authorization)

    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not sess or sess.user_id != payload["user_id"]:
        raise HTTPException(status_code=400, detail="Invalid session")

    chats = (
        db.query(Chat)
        .filter(Chat.session_id == session_id)
        .order_by(Chat.id.asc())
        .all()
    )

    return [
        {
            "id": c.id,
            "role": c.role,
            "content": c.content
        }
        for c in chats
    ]
