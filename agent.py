import json
import os
import asyncio
import functools
import logging
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field, create_model
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage

from prompts import AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


# ==========================================
# RUN ASYNC IN SYNC CONTEXT HELPER
# ==========================================

def run_async_sync(coro) -> Any:
    """Run an async coroutine synchronously, handling whether an event loop is running or not."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


def _make_sync_wrapper(async_func: Callable) -> Callable:
    """Wrap an async function to be callable synchronously."""
    @functools.wraps(async_func)
    def wrapper(**kwargs):
        return run_async_sync(async_func(**kwargs))
    return wrapper


# ==========================================
# TOOL SCHEMA BUILDER (Pydantic v2)
# ==========================================

# Map JSON schema types to Python types
_TYPE_MAP = {
    "integer": int,
    "number": float,
    "boolean": bool,
    "string": str,
}


def _build_args_model(tool_name: str, schema: dict) -> type:
    """Build a Pydantic v2 model from MCP tool's JSON input schema."""
    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))

    fields = {}
    for prop_name, prop_schema in properties.items():
        # Handle anyOf (Optional types like {"anyOf": [{"type": "integer"}, {"type": "null"}]})
        if "anyOf" in prop_schema:
            for option in prop_schema["anyOf"]:
                if option.get("type") != "null":
                    json_type = option.get("type", "string")
                    python_type = _TYPE_MAP.get(json_type, str)
                    break
            else:
                python_type = str
        else:
            json_type = prop_schema.get("type", "string")
            python_type = _TYPE_MAP.get(json_type, str)

        description = prop_schema.get("description", "")

        if prop_name in required_fields:
            fields[prop_name] = (python_type, Field(description=description))
        else:
            default = prop_schema.get("default")
            fields[prop_name] = (Optional[python_type], Field(default=default, description=description))

    model_name = f"{tool_name.title().replace('_', '').replace('-', '')}Args"
    return create_model(model_name, **fields)


# ==========================================
# MCP TOOL WRAPPER
# ==========================================

class MCPToolWrapper:
    """Wraps MCP server tools as LangChain StructuredTools."""

    def __init__(self):
        from mcp_server import mcp as mcp_server
        self._mcp = mcp_server
        self._tools_map = {}

    def _load_tools(self):
        """Load all tools from MCP server."""
        tools = run_async_sync(self._mcp.list_tools())
        for tool in tools:
            self._tools_map[tool.name] = tool

    def get_langchain_tools(self) -> List[StructuredTool]:
        """Convert all MCP tools to LangChain StructuredTools."""
        self._load_tools()
        lc_tools = []

        for tool_name, tool in self._tools_map.items():
            schema = tool.inputSchema

            def make_async_call(name: str):
                async def _call_tool(**kwargs):
                    try:
                        result = await self._mcp.call_tool(name, kwargs)
                        # MCP call_tool returns a tuple: (content_blocks, metadata)
                        # content_blocks is a list of TextContent objects
                        if isinstance(result, tuple):
                            content_blocks = result[0]
                        else:
                            content_blocks = result
                        texts = []
                        for block in content_blocks:
                            if hasattr(block, "text"):
                                texts.append(block.text)
                            else:
                                texts.append(str(block))
                        return "\n".join(texts) if texts else ""
                    except Exception as e:
                        logger.error(f"MCP tool '{name}' failed: {e}")
                        return json.dumps({"type": "error", "title": "Tool Error", "data": {"message": f"Tool '{name}' failed: {str(e)}"}})
                return _call_tool

            async_func = make_async_call(tool_name)
            sync_func = _make_sync_wrapper(async_func)
            args_model = _build_args_model(tool_name, schema)
            description = tool.description or tool_name

            lc_tool = StructuredTool(
                name=tool_name,
                description=description,
                func=sync_func,
                coroutine=async_func,
                args_schema=args_model,
            )
            lc_tools.append(lc_tool)

        return lc_tools


# ==========================================
# DATABASE AGENT
# ==========================================

class DatabaseAgent:
    """Multi-step agentic framework for database queries using LangGraph."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.fallback_key = os.getenv("OPENROUTER_FALLBACK_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")

        self.model = "openai/gpt-oss-20b:free"
        self.llm = self._create_llm(self.api_key)

        self.tools = MCPToolWrapper().get_langchain_tools()
        self.memory: List[Dict[str, str]] = []
        self.agent_graph = None
        self._setup_agent()

    def _create_llm(self, api_key: str) -> ChatOpenAI:
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model=self.model,
            temperature=0,
            max_tokens=2000,
        )

    def _setup_agent(self):
        """Create the LangGraph agent with tools and system prompt."""
        self.agent_graph = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=AGENT_SYSTEM_PROMPT,
        )

    def run(self, question: str) -> Dict[str, Any]:
        """
        Run the agent on a user question.
        Returns dict with answer, structured_data, and steps.
        """
        messages = []
        for msg in self.memory:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=question))

        try:
            result = self.agent_graph.invoke({"messages": messages}, {"recursion_limit": 10})
        except Exception as e:
            if self.fallback_key and ("429" in str(e) or "rate" in str(e).lower()):
                logger.warning("Primary API key rate limited, switching to fallback key")
                self.llm = self._create_llm(self.fallback_key)
                self._setup_agent()
                result = self.agent_graph.invoke({"messages": messages}, {"recursion_limit": 10})
            else:
                raise

        all_messages = result.get("messages", [])
        answer = ""
        # Get the last AIMessage with content (skip ToolMessage results)
        for msg in reversed(all_messages):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                answer = msg.content
                break
        # Fallback: any message with content
        if not answer:
            for msg in reversed(all_messages):
                if hasattr(msg, "content") and msg.content:
                    answer = msg.content
                    break

        # Post-process: if answer is raw JSON, extract a summary
        if answer and answer.strip().startswith("{") and answer.strip().endswith("}"):
            try:
                parsed = json.loads(answer)
                if "count" in parsed and "title" in parsed:
                    count = parsed["count"]
                    title = parsed["title"]
                    answer = f"{count} results for {title}:"
            except json.JSONDecodeError:
                pass

        self.memory.append({"role": "user", "content": question})
        self.memory.append({"role": "assistant", "content": answer})

        if len(self.memory) > 40:
            self.memory = self.memory[-40:]

        structured_data = []
        steps = []
        tool_call_map = {}

        for msg in all_messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tc_id = tc.get("id")
                    step_idx = len(steps)
                    steps.append({
                        "tool": tc.get("name", "unknown"),
                        "tool_input": tc.get("args", {}),
                        "output": "",
                    })
                    if tc_id:
                        tool_call_map[tc_id] = step_idx
            elif hasattr(msg, "tool_call_id") and msg.tool_call_id:
                tc_id = msg.tool_call_id
                content = msg.content if hasattr(msg, "content") else ""

                if tc_id in tool_call_map:
                    idx = tool_call_map[tc_id]
                    steps[idx]["output"] = content
                elif steps:
                    steps[-1]["output"] = content

                parsed = self._parse_tool_output(content)
                if parsed:
                    structured_data.append(parsed)

        return {
            "answer": answer,
            "structured_data": structured_data,
            "steps": steps,
        }

    def _parse_tool_output(self, output: str) -> Optional[Dict]:
        """Try to parse JSON from tool output string."""
        if not isinstance(output, str):
            return None
        try:
            return json.loads(output)
        except (json.JSONDecodeError, TypeError):
            try:
                start = output.index("{")
                end = output.rindex("}") + 1
                return json.loads(output[start:end])
            except (ValueError, json.JSONDecodeError):
                return None
