# intelligence/test_local_llm.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.local_llm import run_local_llm

if __name__ == "__main__":
    test_watchlist = [
        {
            "symbol": "AIFF",
            "desc": "Firefly Neuroscience: new brainwave analysis platform launched targeting neurodiagnostics market"
        },
        {
            "symbol": "MDIA",
            "desc": "MediaCo Holding Inc. reports interim safety data showing promising early results"
        }
    ]

    print("🔍 Envoi de la watchlist au modèle local Mistral...\n")
    output = run_local_llm(test_watchlist)

    print("🧠 Réponse du modèle local Mistral :\n")
    print(output)
