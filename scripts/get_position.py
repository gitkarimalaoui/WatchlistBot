import pyautogui
import time
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")

print("Place ta souris sur un élément Moomoo dans les 5 secondes...")
time.sleep(5)
print("📍 Position capturée :", pyautogui.position())
