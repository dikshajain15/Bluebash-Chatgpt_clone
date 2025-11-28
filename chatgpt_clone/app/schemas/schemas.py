# app/schemas/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List


# -----------------------------
# Auth Schemas
# -----------------------------
class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# Session Schemas
# -----------------------------
class SessionCreateResponse(BaseModel):
    id: int


class SessionListItem(BaseModel):
    id: int
    created_at: Optional[str] = None

    class Config:
        orm_mode = True


# -----------------------------
# Chat Create / Single Response
# -----------------------------
class ChatCreateRequest(BaseModel):
    session_id: int
    message: str


class ChatResponse(BaseModel):
    id: int
    role: str
    content: str


# -----------------------------
# Chat History Fetch Response
# -----------------------------
class ChatItem(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: Optional[str] = None

    class Config:
        orm_mode = True


class ChatListResponse(BaseModel):
    chats: List[ChatItem]
