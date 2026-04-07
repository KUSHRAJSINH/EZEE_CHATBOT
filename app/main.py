from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import upload, chat, stats
from db_store.stats_store import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
   


app = FastAPI(
    title="EzeeChatBot API",
    description="Minimal RAG Chatbot API — upload content, chat with it, track stats.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "EzeeChatBot API"}