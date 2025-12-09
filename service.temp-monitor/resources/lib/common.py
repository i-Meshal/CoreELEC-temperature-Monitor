# -*- coding: utf-8 -*-
# ============================================================
# Author: Meshal (Telegram: @i_Meshal)
# حفظ الحقوق: @i_Meshal
# CoreELEC Temperature Monitor
# Developed by Meshal © 2025
# Licensed under MIT
# https://github.com/i-Meshal/CoreELEC-temperature-Monitor/
# 
# ============================================================
import os, json
import urllib.request

# === إعدادات Relay (قيم ثابتة) ===
RELAY_URL = "https://coreelec-temp.meshal-me.workers.dev/"
API_KEY   = "i_meshal-relay-2025-12"
# ==================================

def read_temps():
    temps = []
    zones_path = "/sys/class/thermal"
    if not os.path.isdir(zones_path):
        return temps
    for name in os.listdir(zones_path):
        if name.startswith("thermal_zone"):
            zpath = os.path.join(zones_path, name)
            try:
                with open(os.path.join(zpath, "type"), "r") as f:
                    tname = f.read().strip()
                with open(os.path.join(zpath, "temp"), "r") as f:
                    milli = int(f.read().strip())
                c = milli // 1000
                temps.append((tname, c))
            except Exception:
                continue
    return temps


def send_via_relay(chat_id, text, parse_mode=None, disable_preview=False):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if disable_preview:
        payload["disable_web_page_preview"] = True

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        RELAY_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status == 200
