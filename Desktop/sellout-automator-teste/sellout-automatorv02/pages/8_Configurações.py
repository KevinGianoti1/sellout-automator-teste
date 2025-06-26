<<<<<<< HEAD
# pages/8_⚙️_Configurações.py
import streamlit as st
from style_config import *

st.set_page_config(page_title="⚙️ Configurações", page_icon="🛠️", layout="wide")

st.markdown("# ⚙️ Configurações")
st.markdown("Aqui você poderá ajustar preferências, notificações ou conexões futuras do sistema.")

st.info("Esta página é apenas um placeholder para configurações futuras do sistema.")

# Simulação de preferências futuras
st.subheader("🔧 Preferências do Sistema (Simulação)")

col1, col2 = st.columns(2)
with col1:
    modo_escuro = st.checkbox("🌙 Ativar modo escuro (visual)")
    notificacoes = st.checkbox("🔔 Receber notificações por email")

with col2:
    linguagem = st.selectbox("🌍 Idioma preferido", ["Português", "Inglês", "Espanhol"])
    timezone = st.selectbox("🕐 Fuso horário", ["UTC-3 (Brasília)", "UTC-4", "UTC-5"])
=======
# pages/8_⚙️_Configurações.py
import streamlit as st
from style_config import *

st.set_page_config(page_title="⚙️ Configurações", page_icon="🛠️", layout="wide")

st.markdown("# ⚙️ Configurações")
st.markdown("Aqui você poderá ajustar preferências, notificações ou conexões futuras do sistema.")

st.info("Esta página é apenas um placeholder para configurações futuras do sistema.")

# Simulação de preferências futuras
st.subheader("🔧 Preferências do Sistema (Simulação)")

col1, col2 = st.columns(2)
with col1:
    modo_escuro = st.checkbox("🌙 Ativar modo escuro (visual)")
    notificacoes = st.checkbox("🔔 Receber notificações por email")

with col2:
    linguagem = st.selectbox("🌍 Idioma preferido", ["Português", "Inglês", "Espanhol"])
    timezone = st.selectbox("🕐 Fuso horário", ["UTC-3 (Brasília)", "UTC-4", "UTC-5"])
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
