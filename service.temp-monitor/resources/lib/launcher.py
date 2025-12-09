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
import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()

choices = ["إرسال رسالة اختبار الآن", "فتح إعدادات الإضافة", "إلغاء"]
dlg = xbmcgui.Dialog()
sel = dlg.select("Temperature Monitor", choices)

if sel == 0:
    xbmc.executebuiltin("RunScript(special://home/addons/service.temp-monitor/resources/lib/send_test.py)")
elif sel == 1:
    xbmcaddon.Addon().openSettings()
else:
    pass
