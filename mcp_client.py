import json
import os
from typing import Any

from dotenv import load_dotenv
from mcp import Client

load_dotenv()

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://127.0.0.1:8000/mcp",
)


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Connect to the MCP server, call one tool, and return its structured result."""
    async with Client(MCP_SERVER_URL) as client:
        result = await client.call_tool(tool_name, arguments)

        if getattr(result, "is_error", False):
            raise RuntimeError(f"MCP tool '{tool_name}' returned an error.")

        structured = getattr(result, "structured_content", None)
        if structured is not None:
            # MCP servers often wrap the structured payload in a result object.
            if isinstance(structured, dict) and "result" in structured:
                return structured["result"]
            return structured

        # Fallback for text-only tool results.
        text_parts = []
        for block in getattr(result, "content", []):
            text = getattr(block, "text", None)
            if text is not None:
                text_parts.append(text)

        text = "\n".join(text_parts)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


async def list_mcp_tools() -> list[str]:
    """Return tool names exposed by the MCP server."""
    async with Client(MCP_SERVER_URL) as client:
        result = await client.list_tools()
        return [tool.name for tool in result.tools]