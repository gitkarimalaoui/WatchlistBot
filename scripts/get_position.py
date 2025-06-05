import pyautogui
import time

print("Place ta souris sur un élément Moomoo dans les 5 secondes...")
time.sleep(5)
print("📍 Position capturée :", pyautogui.position())
