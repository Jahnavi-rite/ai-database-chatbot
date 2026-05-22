from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import time
import uuid

from sqlalchemy import text
from database import engine, SessionLocal
from models import Base
from agent import DatabaseAgent

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# CREATE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)

# ==========================================
# AGENT MANAGER (handles multiple conversations)
# ==========================================

MAX_CONVERSATIONS = 100
_agent_instances: Dict[str, tuple] = {}


def _evict_stale_agents() -> None:
    """Remove the oldest conversation when the limit is reached."""
    if len(_agent_instances) <= MAX_CONVERSATIONS:
        return
    oldest_key = min(_agent_instances, key=lambda k: _agent_instances[k][1])
    logger.info(f"Evicting stale conversation {oldest_key}")
    del _agent_instances[oldest_key]


def get_or_create_agent(conversation_id: Optional[str] = None) -> tuple:
    if conversation_id and conversation_id in _agent_instances:
        agent, _ = _agent_instances[conversation_id]
        _agent_instances[conversation_id] = (agent, time.time())
        return agent, conversation_id

    new_id = conversation_id or str(uuid.uuid4())
    logger.info(f"Initializing DatabaseAgent for conversation {new_id}...")
    agent = DatabaseAgent()
    logger.info(f"Agent ready with {len(agent.tools)} tools")
    _evict_stale_agents()
    _agent_instances[new_id] = (agent, time.time())
    return agent, new_id


# ==========================================
# LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app):
    logger.info("AI Database Chatbot v3.0 starting up...")
    logger.info("MCP tools available: 25+")
    logger.info("Agent: LangGraph ReAct with GPT-4o-mini via OpenRouter")
    logger.info("Multi-step orchestration enabled")
    yield
    _agent_instances.clear()
    logger.info("Shutting down, cleared all agent instances.")


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(title="AI Database Chatbot", version="3.0.0", lifespan=lifespan)

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
# PYDANTIC MODELS
# ==========================================

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question about the database")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for maintaining context")

class ChatResponse(BaseModel):
    answer: str
    structured_data: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    conversation_id: str

class MessageHistory(BaseModel):
    conversation_id: str


# ==========================================
# HOME
# ==========================================

@app.get("/")
async def home():
    return {
        "message": "AI Database Chatbot v3.0 - LangGraph Multi-Step Agent + MCP",
        "version": "3.0.0",
        "endpoints": {
            "chat": "POST /chat - Ask any question about the database",
            "health": "GET /health - Check if the server is running",
            "conversations": "GET /conversations/{conversation_id} - Get conversation history",
        }
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

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
    }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    entry = _agent_instances.get(conversation_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Conversation not found")
    agent, _ = entry
    return {
        "conversation_id": conversation_id,
        "message_count": len(agent.memory),
        "messages": agent.memory,
    }


# ==========================================
# CHAT - Main AI endpoint
# ==========================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask any question about the student database.
    The LangGraph agent will understand natural language,
    call MCP tools multiple times if needed, and return a structured response.
    """
    try:
        agent, conversation_id = get_or_create_agent(request.conversation_id)
        logger.info(f"[{conversation_id}] User question: {request.question}")

        result = agent.run(request.question)

        return ChatResponse(
            answer=result["answer"],
            structured_data=result["structured_data"],
            steps=result["steps"],
            conversation_id=conversation_id,
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
