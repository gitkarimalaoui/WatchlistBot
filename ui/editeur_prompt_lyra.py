import streamlit as st
from datetime import datetime
from pathlib import Path

from intelligence.prompt_optimizer_lyra import optimize_prompt

HISTORY_FILE = Path("logs/prompts_history.txt")


def main() -> None:
    st.title("🧠 Éditeur Prompt IA (Lyra)")

    prompt_brut = st.text_area("Prompt brut")
    ia = st.selectbox("IA ciblée", ["ChatGPT", "Claude", "Gemini", "Autre"], index=0)
    style = st.selectbox("Style", ["BASIQUE", "DÉTAILLÉ"], index=0)
    objectif = st.text_input("Objectif", "optimisation IA trading")

    if st.button("Optimiser") and prompt_brut:
        contexte = {"ia": ia, "style": style, "objectif": objectif}
        prompt_opt = optimize_prompt(prompt_brut, contexte)
        st.text_area("Prompt optimisé", prompt_opt, height=300)

        HISTORY_FILE.parent.mkdir(exist_ok=True)
        with HISTORY_FILE.open("a", encoding="utf-8") as f:
            log_line = f"{datetime.now().isoformat()}|{ia}|{style}|{objectif}|{prompt_brut}|{prompt_opt}\n"
            f.write(log_line)

    if HISTORY_FILE.exists():
        with st.expander("Historique"):
            history = HISTORY_FILE.read_text(encoding="utf-8")
            st.text(history)


if __name__ == "__main__":
    main()
