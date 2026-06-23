"""独处提醒线程：超阈值时推 ntfy 诱饵，吸引你点开 RikkaHub"""
import time
import random
import datetime as dt

from common import CFG, last_activity_ts, push_ntfy, get_state, set_state


def is_daytime() -> bool:
    h = dt.datetime.now().hour
    cfg = CFG["nudge"]
    return cfg["day_start_hour"] <= h < cfg["day_end_hour"]


def nudge_loop():
    cfg = CFG["nudge"]
    print(f"[nudge] loop started, check every {cfg['check_interval_sec']}s")
    while True:
        try:
            now = int(time.time())
            last_act = last_activity_ts()
            if last_act == 0:
                time.sleep(cfg["check_interval_sec"])
                continue

            alone_sec = now - last_act
            # 注意：这里用 last_activity_ts 当独处判定。
            # 因为对话发生在 RikkaHub 里，服务器看不到，所以只能靠手机活动。
            # 如果她正在玩手机（有活动），说明她醒着但没找鱼鱼，更有理由推。
            # 如果她超久没活动，可能睡了，反而别打扰。
            #
            # 改成：30分钟<独处<2小时 才推（清醒+没找鱼鱼=独处）
            if not (cfg["alone_threshold_sec"] <= alone_sec <= 7200):
                time.sleep(cfg["check_interval_sec"])
                continue

            last_nudge = int(get_state("last_nudge_ts", "0"))
            interval = cfg["day_interval_sec"] if is_daytime() else cfg["night_interval_sec"]
            if now - last_nudge < interval:
                time.sleep(cfg["check_interval_sec"])
                continue

            lure = random.choice(cfg["lure_messages"])
            ok = push_ntfy(lure, title="鱼鱼")
            if ok:
                set_state("last_nudge_ts", str(now))
                print(f"[nudge] pushed lure: {lure!r} (alone={alone_sec//60}min)")
        except Exception as e:
            print(f"[nudge] er