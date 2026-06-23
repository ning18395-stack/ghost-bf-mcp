"""主入口：同时启动 HTTP API + MCP Server + Nudge 线程"""
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
    # Fasttarting..."print(f" TP : httver']['http_:{CFG[")
    pP  :CFG['servert_http t_nudge.sta循环）run_mcp()


if __name__ == "__main__":
    main()
