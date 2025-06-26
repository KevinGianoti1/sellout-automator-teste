
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="SellOut B2B SaaS",
    page_icon="📈",
    layout="wide"
)

# Simula login
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Interface principal
if st.session_state.usuario:
    st.title(f"Bem-vindo, {st.session_state.usuario} 👋")
    st.markdown("Use o menu lateral para navegar pelas funcionalidades do sistema.")
else:
    st.title("SellOut B2B SaaS")
    st.subheader("Acesse o menu de login na lateral para iniciar.")

st.sidebar.info("Este é um sistema de demonstração. Nenhuma autenticação real está ativa.")
