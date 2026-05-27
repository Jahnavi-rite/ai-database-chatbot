import os
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text

from database import engine, SessionLocal
from models import Base
from auth.models import User
from auth.seed import seed_users
from auth.routes import router as auth_router
from auth.dependencies import get_current_user, get_db, require_write_access
from agent import DatabaseAgent

# ==========================================
# LOGGING — centralized with file + console
# ==========================================

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Console handler — INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S")
console_handler.setFormatter(console_fmt)

# File handler — DEBUG and above, rotated daily
from logging.handlers import TimedRotatingFileHandler
file_handler = TimedRotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    when="midnight",
    backupCount=7,
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s")
file_handler.setFormatter(file_fmt)

root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

# ==========================================
# CREATE TABLES + SEED USERS
# ==========================================

Base.metadata.create_all(bind=engine)
User.metadata.create_all(bind=engine)
seed_users()

# ==========================================
# AGENT MANAGER
# ==========================================

MAX_CONVERSATIONS = 100
_agent_instances: Dict[str, tuple] = {}  # key -> (agent, timestamp, role)
# Cache key format: "username:conversation_id" — isolates each user's agents


def _evict_stale_agents() -> None:
    if len(_agent_instances) <= MAX_CONVERSATIONS:
        return
    oldest_key = min(_agent_instances, key=lambda k: _agent_instances[k][1])
    logger.info(f"Evicting stale conversation {oldest_key}")
    del _agent_instances[oldest_key]


def get_or_create_agent(username: str, role: str, conversation_id: Optional[str] = None) -> tuple:
    # Cache key is scoped to the user — no cross-user access possible
    cache_key = f"{username}:{conversation_id}" if conversation_id else None

    if cache_key and cache_key in _agent_instances:
        agent, ts, cached_role = _agent_instances[cache_key]
        _agent_instances[cache_key] = (agent, time.time(), cached_role)
        logger.debug(f"Reusing agent for {username} (conversation {conversation_id}, role={cached_role})")
        return agent, conversation_id

    new_id = conversation_id or str(uuid.uuid4())
    logger.info(f"Creating new DatabaseAgent for user={username} role={role} conversation={new_id}")
    agent = DatabaseAgent(role=role)
    logger.info(f"Agent ready: {len(agent.tools)} tools (role={role})")
    new_cache_key = f"{username}:{new_id}"
    _evict_stale_agents()
    _agent_instances[new_cache_key] = (agent, time.time(), role)
    return agent, new_id


# ==========================================
# LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app):
    logger.info("=" * 50)
    logger.info("AI Database Chatbot v4.0 starting up")
    logger.info("Auth: JWT + bcrypt enabled")
    logger.info("Logging: console (INFO) + file (DEBUG)")
    logger.info("=" * 50)
    yield
    _agent_instances.clear()
    logger.info("Shutting down — cleared all agent instances")


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(title="AI Database Chatbot", version="4.0.0", lifespan=lifespan)

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTERS
# ==========================================

app.include_router(auth_router)

# ==========================================
# PYDANTIC MODELS
# ==========================================

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    role: Optional[str] = Field(default=None, description="User role (admin or user). Ignored server-side — enforced from JWT token.")

class ChatResponse(BaseModel):
    answer: str
    structured_data: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    conversation_id: str


# ==========================================
# PUBLIC ENDPOINTS
# ==========================================

@app.get("/")
async def home():
    return {
        "message": "AI Database Chatbot v4.0",
        "version": "4.0.0",
        "endpoints": {
            "login": "POST /auth/login — get JWT token",
            "me": "GET /auth/me — get current user (protected)",
            "chat": "POST /chat — ask questions (protected)",
            "health": "GET /health",
        },
    }


@app.get("/health")
async def health():
    db_ok = False
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning(f"Health check DB probe failed: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass
    return {"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "unavailable"}


# ==========================================
# PROTECTED ENDPOINTS
# ==========================================

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user = Depends(get_current_user),
):
    logger.info(f"[{user.username}] Chat request: {request.question[:80]} (JWT role={user.role}, body role={request.role})")
    if request.role and request.role != user.role:
        logger.warning(f"[{user.username}] Body role '{request.role}' != JWT role '{user.role}'. Using JWT role.")
    try:
        agent, conversation_id = get_or_create_agent(
            username=user.username,
            role=user.role,
            conversation_id=request.conversation_id,
        )
        result = agent.run(request.question)
        logger.info(f"[{user.username}:{conversation_id}] Response generated ({len(result['answer'])} chars)")
        return ChatResponse(
            answer=result["answer"],
            structured_data=result["structured_data"],
            steps=result["steps"],
            conversation_id=conversation_id,
        )
    except Exception as e:
        logger.error(f"[{user.username}] Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user = Depends(get_current_user),
):
    cache_key = f"{user.username}:{conversation_id}"
    entry = _agent_instances.get(cache_key)
    if not entry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    agent, _ = entry
    logger.info(f"[{user.username}] Conversation history requested: {conversation_id}")
    return {
        "conversation_id": conversation_id,
        "message_count": len(agent.memory),
        "messages": agent.memory,
    }
