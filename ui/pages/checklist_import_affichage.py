
import streamlit as st
import pandas as pd
import os
from utils.module_checklist_fusion import charger_sources_checklist, fusionner_tous_les_tickers, generer_checklist_fusionnee
from utils.utils_watchlist import importer_watchlist_txt
from watchlist_panel import render_watchlist_panel

st.set_page_config(page_title="Checklist Fusionnée", layout="wide")
st.title("🧩 Import & Checklist Fusionnée")

# Section d'import manuel depuis un fichier .txt
st.markdown("### 📥 Importer un fichier texte DrJag/KarimAlaoui")
uploaded_txt = st.file_uploader("Dépose ton fichier .txt ici :", type=["txt"])
if uploaded_txt is not None:
    temp_path = os.path.join("data", "watchlist_uploaded_temp.txt")
    with open(temp_path, "wb") as f:
        f.write(uploaded_txt.getbuffer())

    # Appel à l'import
    tickers_ajoutes = importer_watchlist_txt(temp_path)
    if "Erreur" not in tickers_ajoutes[0]:
        st.success(f"✅ {len(tickers_ajoutes)} tickers ajoutés depuis le fichier : {', '.join(tickers_ajoutes)}")
    else:
        st.error(tickers_ajoutes[0])

# Charger les données des différentes sources
sources = charger_sources_checklist()
meta_ia = sources["ia"]
tickers_manuels = sources["manuels"]
rules_auto = sources["rules"]
txt_content = sources["txt_checklist"]
csv_data = sources["csv_checklist"]

with st.expander("📄 Checklist CSV importée (si disponible)", expanded=False):
    if not csv_data.empty:
        st.dataframe(csv_data)
    else:
        st.warning("Aucun fichier CSV valide importé.")

# Fusionner toutes les sources de tickers
tickers_total = fusionner_tous_les_tickers(meta_ia, tickers_manuels)
st.success(f"✅ {len(tickers_total)} tickers fusionnés à partir de toutes les sources.")

# Générer et afficher la checklist fusionnée avec vérification
df_checklist = generer_checklist_fusionnee(meta_ia, rules_auto, tickers_total, tickers_manuels)
st.markdown("### ✅ Checklist combinée avec critères :")
st.dataframe(df_checklist, use_container_width=True)

# Option d'export
st.download_button("💾 Télécharger checklist fusionnée (.csv)", data=df_checklist.to_csv(index=False), file_name="checklist_fusionnee.csv")

render_watchlist_panel()
