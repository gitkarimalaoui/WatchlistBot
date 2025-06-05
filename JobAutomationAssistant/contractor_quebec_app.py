
import streamlit as st
import subprocess
import platform

st.set_page_config(
    page_title="Lanceur d'Applications",
    page_icon="🧭",
    layout="centered"
)

st.title("🧭 Lanceur d'Applications")
st.markdown("Bienvenue dans votre assistant automatisé. Choisissez une application à lancer :")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Assistant Emploi"):
        st.markdown("### Exécution : `app.py`")
        st.markdown("```bash\nstreamlit run app.py```")

with col2:
    if st.button("📄 Contracteur Québec"):
        st.markdown("### Exécution : `contractor_quebec_app.py`")
        st.markdown("```bash\nstreamlit run contractor_quebec_app.py```")

st.markdown("---")
st.markdown("ℹ️ Lancez manuellement la commande ci-dessous dans votre terminal :")
st.code("streamlit run app.py
streamlit run contractor_quebec_app.py", language="bash")
