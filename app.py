"""Main entry: starts HTTP API, MCP server, and nudge worker."""
import threading

import uvicorn

from common import CFG, init_db
from http_api import http_app
from mcp_server import mcp
from nudger import nudge_loop


def run_http():
    uvicorn.run(
        http_app,
        host=CFG["server"]["http_host"],
        port=CFG["server"]["http_port"],
        log_level="info",
    )


def run_mcp():
    # FastMCP uses SSE transport. The URL is http://host:port/sse
    mcp.run(transport="sse")


def main():
    init_db()
    http_host = CFG["server"]["http_host"]
    http_port = CFG["server"]["http_port"]
    mcp_host = CFG["server"]["mcp_host"]
    mcp_port = CFG["server"]["mcp_port"]

    print("=" * 50)
    print("Ghost-BF Server starting...")
    print(f"  HTTP : http://{http_host}:{http_port}")
    print(f"  MCP  : http://{mcp_host}:{mcp_port}/sse")
    print("=" * 50)

    t_http = threading.Thread(target=run_http, daemon=True, name="http")
    t_nudge = threading.Thread(target=nudge_loop, daemon=True, name="nudge")
    t_http.start()
    t_nudge.start()

    run_mcp()


if __name__ == "__main__":
    main()
