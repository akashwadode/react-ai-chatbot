from fastapi import APIRouter, Depends
from pydantic import BaseModel
from modules.link.router import validate_signed_request
from modules.chat.service import handle_chat

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat_ai(body: ChatRequest, context=Depends(validate_signed_request)):
    pid_hash = context["pid"]
    return handle_chat(pid_hash, body.question)