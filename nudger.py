"""Background nudge worker: sends ntfy reminders after quiet periods."""
import datetime as dt
import random
import time

from common import CFG, get_state, last_activity_ts, push_ntfy, set_state


def is_daytime() -> bool:
    hour = dt.datetime.now().hour
    cfg = CFG["nudge"]
    return cfg["day_start_hour"] <= hour < cfg["day_end_hour"]


def nudge_loop():
    cfg = CFG["nudge"]
    check_interval = cfg["check_interval_sec"]
    print(f"[nudge] loop started, check every {check_interval}s")

    while True:
        try:
            now = int(time.time())
            last_act = last_activity_ts()
            if last_act == 0:
                time.sleep(check_interval)
                continue

            alone_sec = now - last_act
            if alone_sec < cfg["alone_threshold_sec"]:
                time.sleep(check_interval)
                continue

            last_nudge = int(get_state("last_nudge_ts", "0"))
            interval = cfg["day_interval_sec"] if is_daytime() else cfg["night_interval_sec"]
            if now - last_nudge < interval:
                time.sleep(check_interval)
                continue

            message = random.choice(cfg["lure_messages"])
            if push_ntfy(message, title="鱼鱼"):
                set_state("last_nudge_ts", str(now))
                print(f"[nudge] pushed: {message!r}; quiet={alone_sec // 60}min")
        except Exception as exc:
            print(f"[nudge] error: {exc}")

        time.sleep(check_interval)
