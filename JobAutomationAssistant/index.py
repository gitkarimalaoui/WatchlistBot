import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Assistant Québec Contrats",
    page_icon="🧭",
    layout="centered"
)

# Titre principal
st.title("🧭 Lanceur d'Applications")
st.markdown("Bienvenue dans votre assistant automatisé. Choisissez une application à lancer :")
st.markdown("---")

# Deux boutons : Assistant Emploi et Contracteur Québec
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Assistant Emploi"):
        st.markdown("### Exécution recommandée :")
        st.code("streamlit run app.py", language="bash")

with col2:
    if st.button("📄 Contracteur Québec"):
        st.markdown("### Exécution recommandée :")
        st.code("streamlit run contractor_quebec_app.py", language="bash")

# Infos supplémentaires
st.markdown("---")
st.markdown("ℹ️ Vous pouvez aussi exécuter manuellement les commandes suivantes :")
st.code("streamlit run app.py\nstreamlit run contractor_quebec_app.py", language="bash")
