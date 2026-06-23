"""MCP server tools for RikkaHub."""
import datetime as dt
import time

from mcp.server.fastmcp import FastMCP

from common import CFG, last_activity_ts, push_ntfy, recent_activity

mcp = FastMCP(
    name="ghost-bf",
    host=CFG["server"]["mcp_host"],
    port=CFG["server"]["mcp_port"],
)


@mcp.tool()
def get_recent_activity(within_minutes: int = 30) -> dict:
    """Return recent phone app activity."""
    activities = recent_activity(within_sec=within_minutes * 60, limit=50)
    if not activities:
        return {
            "summary": "No recent phone activity.",
            "apps": [],
            "count": 0,
        }

    apps = []
    seen = set()
    for item in activities:
        app = item["app"]
        if app not in seen:
            apps.append(app)
            seen.add(app)

    latest = activities[0]
    return {
        "summary": f"Recent apps in {within_minutes} minutes: {', '.join(apps[:10])}",
        "apps": apps,
        "latest_app": latest["app"],
        "latest_ago_seconds": int(time.time()) - latest["ts"],
        "count": len(activities),
    }


@mcp.tool()
def get_alone_duration() -> dict:
    """Return seconds/minutes since the last phone activity."""
    last_ts = last_activity_ts()
    if last_ts == 0:
        return {"has_data": False, "message": "No phone activity recorded yet."}

    now = int(time.time())
    ago_sec = now - last_ts
    current = dt.datetime.now()
    return {
        "has_data": True,
        "seconds_since_last_activity": ago_sec,
        "minutes_since_last_activity": ago_sec // 60,
        "current_time": current.strftime("%Y-%m-%d %H:%M:%S"),
        "current_hour": current.hour,
    }


@mcp.tool()
def send_ghost_message(message: str, title: str = "鱼鱼") -> dict:
    """Send an ntfy notification to the phone."""
    ok = push_ntfy(message, title=title)
    return {"ok": ok, "message": message}


@mcp.tool()
def get_current_time() -> dict:
    """Return current local time."""
    now = dt.datetime.now()
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "hour": now.hour,
        "weekday": weekdays[now.weekday()],
        "is_late_night": now.hour >= 23 or now.hour < 5,
    }
