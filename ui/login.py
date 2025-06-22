import streamlit as st
from security.auth_manager import authenticate_user

st.set_page_config(page_title="Login")

st.title("🔐 Connexion")

if "user_role" in st.session_state:
    st.info(f"Connect\u00e9 en tant que : {st.session_state['user_role']}")

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    success, role = authenticate_user(username, password)
    if success:
        st.session_state["user_role"] = role
        st.success(f"Authentification r\u00e9ussie ({role})")
        st.rerun()
    else:
        st.error("\u00c9chec de l'authentification")
