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
import xbmc, xbmcaddon
import xbmcgui

# استيراد الدوال المشتركة من resources/lib/common.py
try:
    from common import read_temps, send_via_relay
except Exception as e:
    # في حال مسار المكتبة غير موجود في sys.path، نحاول إضافته يدويًا
    import sys, os
    ADDON = xbmcaddon.Addon()
    base_path = ADDON.getAddonInfo('path')
    try:
        import xbmcvfs
        translate_path = xbmcvfs.translatePath
    except Exception:
        translate_path = xbmc.translatePath
    base_path = translate_path(base_path)
    lib_path = os.path.join(base_path, 'resources', 'lib')
    if lib_path not in sys.path:
        sys.path.append(lib_path)
    from common import read_temps, send_via_relay

addon_id = 'service.temp-monitor'
try:
    ADDON = xbmcaddon.Addon()  # داخل سياق الإضافة
except RuntimeError:
    ADDON = xbmcaddon.Addon(id=addon_id)  # fallback خارج السياق


def main():
    chat_id = ADDON.getSetting("chat_id").strip()
    if not chat_id:
        xbmcgui.Dialog().notification("Temperature Monitor", "يرجى ضبط Chat ID أولاً", xbmcgui.NOTIFICATION_ERROR, 4000)
        return

    temps = read_temps()
    if temps:
        lines = "\n".join([f"{name}: {val}°C" for name, val in temps])
        msg = "رسالة اختبار — لا تتطلب إجراء\n" + lines
    else:
        msg = "رسالة اختبار — لا تتطلب إجراء (تعذر قراءة الحساسات)"

    try:
        ok = send_via_relay(chat_id, msg, parse_mode="HTML", disable_preview=True)
        if ok:
            xbmcgui.Dialog().notification("Temperature Monitor", "تم إرسال رسالة الاختبار ✅", xbmcgui.NOTIFICATION_INFO, 4000)
        else:
            xbmcgui.Dialog().notification("Temperature Monitor", "فشل إرسال رسالة الاختبار ❌", xbmcgui.NOTIFICATION_ERROR, 4000)
    except Exception as e:
        xbmcgui.Dialog().notification("Temperature Monitor", f"خطأ: {e}", xbmcgui.NOTIFICATION_ERROR, 5000)


if __name__ == '__main__':
    main()
