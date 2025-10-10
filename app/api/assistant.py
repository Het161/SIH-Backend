from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ml.chatbot import AIChatbot

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])
chatbot = AIChatbot()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    answer = chatbot.chat(request.message)
    return ChatResponse(response=answer)
