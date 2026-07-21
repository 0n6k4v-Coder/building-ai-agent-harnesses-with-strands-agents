import os
import json
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

class MCPManager:
    def __init__(self, config_path=".agents/settings/mcp.json"):
        self.config_path = config_path
        self.servers = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mcpServers", {})
        return {}

    def get_clients(self) -> dict:
        clients = {}
        for name, config in self.servers.items():
            try:
                server_type = config.get("type", "stdio")
                
                if server_type == "stdio":
                    params = StdioServerParameters(
                        command=config.get("command"),
                        args=config.get("args", []),
                        env=config.get("env", None)
                    )
                    clients[name] = MCPClient(lambda p=params: stdio_client(p))
                    
                elif server_type == "sse":
                    url = config.get("url")
                    headers = config.get("headers", {})
                    if not url:
                        continue
                    clients[name] = MCPClient(lambda u=url, h=headers: sse_client(url=u, headers=h))
                    
                elif server_type in ["http", "streamable_http"]:
                    url = config.get("url")
                    headers = config.get("headers", {})
                    if not url:
                        continue
                    clients[name] = MCPClient(lambda u=url, h=headers: streamablehttp_client(url=u, headers=h))
                    
                else:
                    print(f"⚠️ Unsupported MCP server type: {server_type} for {name}")
                    
            except Exception as e:
                print(f"⚠️ Failed to prepare MCP client for {name}: {e}")
                
        return clients