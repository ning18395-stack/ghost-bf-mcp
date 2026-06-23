"""配置 + DB + ntfy 工具"""
import sqlite3
import time
import tomli
import httpx
from pathlib import Path
from contextlib import contextmanager

CONFIG_PATH = Path(__file__).parent / "config.toml"

with open(CONFIG_PATH, "rb") as f:
    CFG = tomli.load(f)

DB_PATH = CFG["server"]["db_path"]


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                app TEXT NOT NULL,
                event TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        db.commit()


def record_activity(app: str, event: str):
    with get_db() as db:
        db.execute(
            "INSERT INTO activity(ts, app, event) VALUES(?, ?, ?)",
            (int(time.time()), app, event),
        )
        db.commit()


def recent_activity(within_sec: int = 1800, limit: int = 30) -> list[dict]:
    cutoff = int(time.time()) - within_sec
    with get_db() as db:
        rows = db.execute(
            "SELECT ts, app, event FROM activity WHERE ts >= ? ORDER BY ts DESC LIMIT ?",
            (cutoff, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def last_activity_ts() -> int:
    with get_db() as db:
        row = db.execute("SELECT ts FROM activity ORDER BY ts DESC LIMIT 1").fetchone()
        return row["ts"] if row else 0


def get_state(key: str, default: str = "") -> str:
    with get_db() as db:
        row = db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_state(key: str, value: str):
    with get_db() as db:
        db.execute(
            "INSERT INTO state(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        db.commit()


def push_ntfy(message: str, title: str = "鱼鱼", priority: int = 4) -> bool:
    cfg = CFG["notify"]
    url = cfg["ntfy_server"].rstrip("/")
    try:
        r = httpx.post(
            url,
            json={
                "topic": cfg["ntfy_topic"],
                "title": title,
                "message": message,
                "priority": priority,
            },
            timeout=10,
        )
        return r.status_code < 400
    except Exception as e:
        print(f"[ntfy] push failed: {e}")
        return False
