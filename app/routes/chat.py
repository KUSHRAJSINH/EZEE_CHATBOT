import time
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse # for streaming
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from model_schema.schemas import ChatRequest
from services.retriever import retrieve_chunks #retrieve_chunks
from services.prompt import prompt
from services.llm import llm_model
from db_store.stats_store import record_stat

router = APIRouter(tags=["chat"])

# pattern to detect unanswered / out-of-context responses (per plan spec)
UNANSWERED_PATTERN = "i couldn't find information"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:

    # ── Step 1: Retrieve relevant context chunks ──────────────────────────────
    try:
        #breakpoint()
        chunks = retrieve_chunks(query=request.user_message, bot_id=request.bot_id, k=5)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Could not retrieve from bot '{request.bot_id}': {str(e)}"
        )

    context = "\n\n".join(chunks) if chunks else "No relevant context found."

    # ── Step 2: Build LangChain message list ─────────────────────────────────
    # System message with injected context (from prompt template)
    formatted = prompt.format_messages(context=context, question=request.user_message)
    system_content = formatted[0].content  # SystemMessage content

    lc_messages = [SystemMessage(content=system_content)]

    # Append conversation history
    for msg in request.conversation_history:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        else:
            lc_messages.append(AIMessage(content=msg.content))

    # Current user turn
    lc_messages.append(HumanMessage(content=request.user_message))

    llm = llm_model()

    # ── Step 3: Stream response via SSE ──────────────────────────────────────
    async def token_stream() -> AsyncGenerator[str, None]:
        full_response: list[str] = []
        start_time = time.time()
        input_tokens = 0
        output_tokens = 0

        try:
            async for chunk in llm.astream(lc_messages):
                token = chunk.content
                if token:
                    full_response.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"

                # Collect token usage if the provider returns it mid-stream
                if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                    input_tokens  += chunk.usage_metadata.get("input_tokens", 0)
                    output_tokens += chunk.usage_metadata.get("output_tokens", 0)

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        finally:
            # ── Step 4: Persist stats ─────────────────────────────────────────
            latency_ms = (time.time() - start_time) * 1000
            complete_response = "".join(full_response)

            # Graceful-fallback detection: did the model decline to answer?
            is_unanswered = UNANSWERED_PATTERN in complete_response.lower()

            # Rough token estimate if streaming didn't yield usage metadata
            if input_tokens == 0:
                input_tokens = sum(len(m.content) for m in lc_messages) // 4
            if output_tokens == 0:
                output_tokens = max(len(complete_response) // 4, 1)

            try:
                await record_stat(
                    bot_id=request.bot_id,
                    latency_ms=round(latency_ms, 2),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    is_unanswered=is_unanswered,
                )
            except Exception:
                pass  
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
