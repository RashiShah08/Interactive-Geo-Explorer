from fastapi import APIRouter

from server.schemas import ChatIn, ChatOut
from src.guide.answer import answer

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn) -> ChatOut:
    """Answer from the local corpus. No API key, no network call, no cost —
    so this route is public like the rest of the atlas."""
    question = next(
        (message.content for message in reversed(payload.messages) if message.role == "user"),
        "",
    )
    reply = answer(question)
    return ChatOut(ok=True, reply=reply.text, citations=reply.citations)
