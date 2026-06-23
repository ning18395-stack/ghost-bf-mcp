"""FastAPI HTTP 端：接收 Macrodroid 上报"""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from common import CFG, record_activity, recent_activity, push_ntfy

http_app = FastAPI(title="Ghost-BF HTTP")


class ActivityIn(BaseModel):
    app: str
    event: str = "switch"


@http_app.post("/phone/activity")
def phone_activity(data: ActivityIn, x_auth_token: str = Header(default="")):
    if x_auth_token != CFG["phone"]["secret"]:
        raise HTTPException(401, "bad token")
    record_activity(data.app, data.event)
    return {"ok": True}


@http_app.get("/activity")
def get_activity(within_sec: int = 1800):
    return {"activity": recent_activity(within_sec)}


@http_app.post("/test/ntfy")
def test_ntfy():
    ok = push_ntfy("测试推送", title="测试")
    return {"ok": ok}


@http_app.get("/health")
def health():
    return {"ok": True}
