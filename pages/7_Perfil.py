import streamlit as st
from style_config import *

st.set_page_config(page_title="👤 Perfil", page_icon="🧑", layout="wide")

st.markdown("# 👤 Perfil do Usuário")

# Simula usuário logado
usuario = st.session_state.get("usuario", "marco@teste.com")

st.markdown(f"**Email:** {usuario}")
st.markdown("**Cargo:** Representante Comercial")
st.markdown("**Empresa:** MF Ferramentas")
st.markdown("**Região de Atuação:** Sul/Sudeste")

st.info("Essas informações são fictícias. No futuro, aqui poderemos integrar um perfil dinâmico com dados reais do usuário e suas configurações pessoais.")
