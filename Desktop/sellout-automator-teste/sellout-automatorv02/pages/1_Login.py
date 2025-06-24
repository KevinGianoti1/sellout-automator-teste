import streamlit as st

# ⛔️ Nada pode vir antes deste comando
st.set_page_config(page_title="🔐 Login", layout="wide")

# ✅ Agora pode importar estilos e outros
from style_config import *

st.markdown("# 🔐 Login")

# Formulário
with st.form("login_form"):
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    login = st.form_submit_button("Entrar")

    if login:
        if email and senha:
            st.success("Login visual simulado com sucesso!")
            st.session_state["logado"] = True
            st.session_state["usuario"] = email
        else:
            st.error("Preencha todos os campos para entrar.")
