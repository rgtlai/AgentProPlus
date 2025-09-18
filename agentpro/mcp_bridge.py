from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import asyncio

try:
    # Client-side MCP SDK
    from mcp.client.stdio import StdioServer
    from mcp.client.session import ClientSession
except Exception:  # pragma: no cover
    StdioServer = None  # type: ignore
    ClientSession = None  # type: ignore


class MCPNotAvailableError(RuntimeError):
    pass


class MCPClientManager:
    """Manages connections to one or more MCP servers and exposes tool calls.

    servers_config example (stdio):
    [
        {"id": "local-search", "command": "python", "args": ["-m", "my_search_mcp"]},
        {"id": "math", "command": "python", "args": ["mcp_server.py"]},
    ]
    """

    def __init__(self, servers_config: List[Dict[str, Any]]):
        self._config = servers_config or []
        self._servers: Dict[str, Any] = {}
        self._sessions: Dict[str, ClientSession] = {}
        self._loop = None

    # ---------- public sync facade ----------
    def start(self) -> None:
        self._ensure_sdk()
        asyncio.run(self._astart())

    def stop(self) -> None:
        if not self._sessions:
            return
        asyncio.run(self._astop())

    def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return all tools per server id: {server_id: [{name, description, schema}, ...]}"""
        return asyncio.run(self._alist_all_tools())

    def call_tool(self, server_id: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        return asyncio.run(self._acall_tool(server_id, tool_name, arguments or {}))

    # ---------- async core ----------
    async def _astart(self) -> None:
        self._ensure_sdk()
        for entry in self._config:
            sid = entry.get("id")
            command = entry.get("command")
            args = entry.get("args", [])
            if not sid or not command:
                continue
            server = StdioServer(command=command, args=args)  # type: ignore[arg-type]
            stream = await server.__aenter__()
            session = ClientSession(stream)
            await session.__aenter__()
            await session.initialize()
            self._servers[sid] = server
            self._sessions[sid] = session

    async def _alist_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        tools_map: Dict[str, List[Dict[str, Any]]] = {}
        for sid, session in self._sessions.items():
            tools = await session.list_tools()
            items: List[Dict[str, Any]] = []
            for t in tools.tools:  # type: ignore[attr-defined]
                items.append({
                    "name": t.name,
                    "description": getattr(t, "description", ""),
                    "input_schema": getattr(t, "inputSchema", None) or getattr(t, "input_schema", None),
                })
            tools_map[sid] = items
        return tools_map

    async def _acall_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        session = self._sessions.get(server_id)
        if not session:
            raise RuntimeError(f"MCP server not connected: {server_id}")
        result = await session.call_tool(tool_name, arguments=arguments)
        # result may include multiple outputs; coalesce to text where possible
        # FastMCP returns a list of content parts; grab text bodies
        try:
            outputs = []
            for item in getattr(result, "content", []) or []:
                text = getattr(item, "text", None) or getattr(item, "value", None)
                if text is not None:
                    outputs.append(text)
            if outputs:
                return "\n".join(map(str, outputs))
        except Exception:
            pass
        return result

    async def _astop(self) -> None:
        for sid, session in list(self._sessions.items()):
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
            self._sessions.pop(sid, None)
        for sid, server in list(self._servers.items()):
            try:
                await server.__aexit__(None, None, None)
            except Exception:
                pass
            self._servers.pop(sid, None)

    def _ensure_sdk(self) -> None:
        if StdioServer is None or ClientSession is None:
            raise MCPNotAvailableError(
                "The 'mcp' package is required for MCP integration. Install with: pip install mcp"
            )

