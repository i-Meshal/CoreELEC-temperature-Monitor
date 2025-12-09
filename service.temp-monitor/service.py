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
import os
from datetime import datetime
import xbmc, xbmcaddon

try:
    import xbmcvfs
    translate_path = xbmcvfs.translatePath
except Exception:
    translate_path = xbmc.translatePath

# ضمان توفر resources/lib في sys.path ثم الاستيراد من common
import sys
ADDON = xbmcaddon.Addon()
base_path = ADDON.getAddonInfo('path')
base_path = translate_path(base_path)
lib_path = os.path.join(base_path, 'resources', 'lib')
if lib_path not in sys.path:
    sys.path.append(lib_path)

from common import read_temps, send_via_relay

# يمكنك إبقاء USE_RELAY هنا لأنه سلوك محلي للخدمة
USE_RELAY = True

PROFILE = translate_path(ADDON.getAddonInfo('profile'))
try:
    os.makedirs(PROFILE, exist_ok=True)
except Exception:
    pass

COUNTER_FILE = os.path.join(PROFILE, 'temp_alert_count.txt')
DATE_FILE    = os.path.join(PROFILE, 'temp_alert_date.txt')

# إعدادات قابلة للتحديث Live
state = {
    'chat_id': '',
    'threshold': 52,
    'daily_limit': 10,
    'interval_secs': 600,
    'show_details': True,
}


def load_settings():
    state['chat_id']       = ADDON.getSetting("chat_id").strip()
    state['threshold']     = int(ADDON.getSetting("temp_threshold") or "52")
    state['daily_limit']   = int(ADDON.getSetting("daily_limit") or "10")
    state['interval_secs'] = int(ADDON.getSetting("interval_secs") or "600")
    state['show_details']  = ADDON.getSettingBool("show_details")


def load_int(path, default=0):
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        return default


def save_text(path, text):
    try:
        with open(path, "w") as f:
            f.write(str(text))
    except Exception:
        pass


class SettingsMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        try:
            load_settings()
            xbmc.log("[temp-monitor] Settings reloaded live", xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f"[temp-monitor] Failed to reload settings: {e}", xbmc.LOGERROR)


def main_loop():
    load_settings()
    if not state['chat_id']:
        xbmc.log("[temp-monitor] Chat ID not set", xbmc.LOGWARNING)
    monitor = SettingsMonitor()

    while not monitor.abortRequested():
        # reset per-day counter (daily)
        today = datetime.now().strftime("%Y-%m-%d")
        last_day = ""
        try:
            with open(DATE_FILE, "r") as f:
                last_day = f.read().strip()
        except Exception:
            pass
        if last_day != today:
            save_text(DATE_FILE, today)
            save_text(COUNTER_FILE, "0")

        alert_count = load_int(COUNTER_FILE, 0)
        temps = read_temps()
        max_temp = max([t for _, t in temps], default=0)

        if state['chat_id'] and max_temp >= state['threshold'] and alert_count < state['daily_limit']:
            if state['show_details'] and temps:
                lines = "\n".join([f"{name}: {val}°C" for name, val in temps])
                msg = f"⚠️ تحذير: الحرارة مرتفعة (≥{state['threshold']}°C)\n{lines}"
            else:
                msg = f"⚠️ تحذير: الحرارة {max_temp}°C (حدّك {state['threshold']}°C)"

            if USE_RELAY:
                try:
                    if send_via_relay(state['chat_id'], msg, parse_mode="HTML", disable_preview=True):
                        save_text(COUNTER_FILE, str(alert_count + 1))
                except Exception as e:
                    xbmc.log(f"[temp-monitor] Relay send error: {e}", xbmc.LOGERROR)
            else:
                xbmc.log("[temp-monitor] Relay disabled or not configured", xbmc.LOGWARNING)

        if monitor.waitForAbort(state['interval_secs']):
            break


if __name__ == "__main__":
    main_loop()
