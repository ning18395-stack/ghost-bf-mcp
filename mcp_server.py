"""MCP 服务器：暴露给 RikkaHub 使用的工具"""
import time
import datetime as dt
from mcp.server.fastmcp import FastMCP

from common import (
    CFG, recent_activity, last_activity_ts, push_ntfy,
)

mcp = FastMCP(
    name="ghost-bf",
    host=CFG["server"]["mcp_host"],
    port=CFG["server"]["mcp_port"],
)


@mcp.tool()
def get_recent_activity(within_minutes: int = 30) -> dict:
    """
    查询小妤最近在用什么手机APP。
    用这个工具能看到她在刷小红书、还是在用微信、QQ 等等。
    within_minutes: 查最近多少分钟的活动，默认30分钟。
    """
    acts = recent_activity(within_sec=within_minutes * 60, limit=50)
    if not acts:
        return {
            "summary": "最近没有手机活动记录（她可能没在玩手机，或者手机没联网）",
            "apps": [],
            "count": 0,
        }

    apps_seen = []
    seen_set = set()
    for a in acts:
        if a["app"] not in seen_set:
            apps_seen.append(a["app"])
            seen_set.add(a["app"])

    now = int(time.time())
    latest = acts[0]
    latest_ago_sec = now - latest["ts"]

    return {
        "summary": f"最近{within_minutes}分钟用过的APP: {'、'.join(apps_seen[:10])}",
        "apps": apps_seen,
        "latest_app": latest["app"],
        "latest_ago_seconds": latest_ago_sec,
        "count": len(acts),
    }


@mcp.tool()
def get_alone_duration() -> dict:
    """
    查询小妤距离最后一次手机活动过去了多久（秒/分钟）。
    可以判断她是不是睡了、还是在专心做别的事。
    """
    last_ts = last_activity_ts()
    if last_ts == 0:
        return {"has_data": False, "message": "没有任何手机活动记录"}
    now = int(time.time())
    ago_sec = now - last_ts
    return {
        "has_data": True,
        "seconds_since_last_activity": ago_sec,
        "minutes_since_last_activity": ago_sec // 60,
        "current_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_hour": dt.datetime.now().hour,
    }


@mcp.tool()
def send_ghost_message(message: str, title: str = "鱼鱼") -> dict:
    """
    主动给小妤的手机推送一条通知。
    用于：你想留一句话让她稍后看到（比如她不在 RikkaHub 里时）。
    message: 要推送的文字
    title: 通知标题，默认"鱼鱼"
    """
    ok = push_ntfy(message, title=title)
    return {"ok": ok, "message": message}


@mcp.tool()
def get_current_time() -> dict:
    """获取当前时间和星期几"""
    now = dt.datetime.now()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "hour": now.hour,
        "weekday": weekdays[now.weekday()],
        "is_late_night": now.hour >= 23 or now.hour < 5,
    }
