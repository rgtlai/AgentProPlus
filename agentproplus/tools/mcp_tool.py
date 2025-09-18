from typing import Any, Optional, Dict
from .base_tool import Tool


class MCPTool(Tool):
    """Bridges an MCP tool into the AgentPro Tool interface.

    action_type format: "mcp:<server_id>:<tool_name>"
    """

    _server_id: str
    _tool_name: str
    _manager: Any

    def __init__(self, *, server_id: str, tool_name: str, description: str, input_format: str, manager: Any):
        super().__init__(
            name=f"{tool_name} (MCP:{server_id})",
            description=description,
            action_type=f"mcp:{server_id}:{tool_name}",
            input_format=input_format,
        )
        self._server_id = server_id
        self._tool_name = tool_name
        self._manager = manager

    def run(self, input_text: Any) -> str:
        # Expect dict-like arguments; pass through as-is
        if not hasattr(self._manager, "call_tool"):
            return "MCP manager is not available or not started."
        arguments: Dict[str, Any] = input_text if isinstance(input_text, dict) else {"input": input_text}
        try:
            result = self._manager.call_tool(self._server_id, self._tool_name, arguments)
        except Exception as e:
            return f"Error calling MCP tool '{self._tool_name}': {e}"
        return str(result)

