import pyautogui
import pyperclip
import time
import sys
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_moomoo.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def executer_ordre(ticker, prix, quantite):
    print("⏳ Préparation... Veuillez ouvrir Moomoo maintenant (5 secondes)")
    time.sleep(5)

    config = load_config()
    pyautogui.FAILSAFE = True
    print(f"🚀 Envoi de l'ordre : {quantite} x {ticker} à {prix}$")

    # Étape 0 : Clic sur le cadenas
    print("🔒 Clic sur le cadenas pour déclencher la fenêtre de code...")
    pyautogui.click(**config["lock_toggle"])
    time.sleep(2.5)

    # Étape 1 : Double clic dans le champ de saisie
    print("🖱️ Double clic dans le champ de saisie...")
    pyautogui.click(**config["unlock_input"], clicks=2, interval=0.2)
    time.sleep(0.5)

    # Étape 2 : Saisie chiffre par chiffre
    print("⌨️ Saisie chiffre par chiffre...")
    for c in config["unlock_code"]:
        pyautogui.press(c)
        time.sleep(0.2)
    time.sleep(1.5)

    # Étape 3 : Recherche ticker
    print("🔍 Recherche du ticker...")
    pyautogui.click(**config["search"])
    time.sleep(0.5)
    pyperclip.copy(ticker)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)

    # Étape 4 : Quick Trade
    print("⚙️ Quick Trade...")
    pyautogui.click(**config["quick_trade"])
    time.sleep(1.5)

    # Étape 5 : Quantité
    print("🔢 Saisie de la quantité...")
    pyautogui.click(**config["quantity"])
    time.sleep(0.3)
    pyperclip.copy(str(quantite))
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Étape 6 : Prix
    print("💵 Saisie du prix...")
    pyautogui.click(**config["price"])
    time.sleep(0.3)
    pyperclip.copy(str(prix))
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Étape 7 : Clic Buy
    print("🟢 Clic sur Buy...")
    pyautogui.click(**config["buy"])
    time.sleep(0.7)

    # Étape 8 : Submit
    print("✅ Clic sur Submit...")
    pyautogui.click(**config["submit"])
    time.sleep(0.5)

    # Étape 9 : Fermer la confirmation
    print("❌ Fermeture de la confirmation d'ordre...")
    pyautogui.click(x=1835, y=162)
    time.sleep(0.5)

    print("✅ Ordre envoyé avec succès.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Utilisation : python scripts/executer_ordre_moomoo.py TICKER PRIX QUANTITÉ")
        sys.exit(1)

    ticker = sys.argv[1]
    prix = float(sys.argv[2])
    quantite = int(sys.argv[3])

    executer_ordre(ticker, prix, quantite)