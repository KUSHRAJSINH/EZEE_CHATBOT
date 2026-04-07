from pydantic import BaseModel, Field
from typing import List, Literal


class UploadResponse(BaseModel):
    bot_id: str


# ── Chat ──────────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """
    Request body for POST /chat.
    """
    bot_id: str
    user_message: str
    conversation_history: List[Message] = Field(
        default_factory=list,
        description="Previous messages in chronological order"
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    bot_id: str
    total_messages: int
    average_latency_ms: float
    estimated_token_cost_usd: float
    unanswered_questions: int
