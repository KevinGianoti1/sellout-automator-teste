
# pages/8⚙️_Configurações.py
import streamlit as st

st.set_page_config(page_title="⚙️ Configurações", page_icon="🛠️", layout="wide")

from style_config import *

st.markdown("""
    <style>
        .config-card {
            background-color: #f5f5f5;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .config-card h3 {
            margin-bottom: 1rem;
            color: #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("# ⚙️ Configurações")
st.caption("Ajuste suas preferências de sistema, notificações, integrações e permissões de usuário.")

# 🔧 Preferências de Interface
st.markdown("""
    <div class='config-card'>
        <h3>🔧 Preferências de Interface</h3>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    modo_escuro = st.checkbox("🌙 Ativar modo escuro (visual)", value=st.session_state.get("modo_escuro", False))
    notificacoes = st.checkbox("🔔 Receber notificações por email", value=st.session_state.get("notificacoes", False))
with col2:
    linguagem = st.selectbox("🌍 Idioma preferido", ["Português", "Inglês", "Espanhol"], index=["Português", "Inglês", "Espanhol"].index(st.session_state.get("linguagem", "Português")))
    timezone = st.selectbox("🕐 Fuso horário", ["UTC-3 (Brasília)", "UTC-4", "UTC-5"], index=["UTC-3 (Brasília)", "UTC-4", "UTC-5"].index(st.session_state.get("timezone", "UTC-3 (Brasília)")))

st.session_state["modo_escuro"] = modo_escuro
st.session_state["notificacoes"] = notificacoes
st.session_state["linguagem"] = linguagem
st.session_state["timezone"] = timezone

if st.button("💾 Salvar Configurações"):
    st.success("✅ Preferências salvas com sucesso!")

st.markdown("</div>", unsafe_allow_html=True)

# 🔐 Gerenciamento de Usuários e Permissões
st.markdown("""
    <div class='config-card'>
        <h3>👥 Gerenciamento de Usuários e Permissões</h3>
""", unsafe_allow_html=True)

usuarios = {
    "marco@teste.com": {"perfil": "admin", "regiao": "Sul/Sudeste"},
    "joao@teste.com": {"perfil": "vendedor", "regiao": "Sudeste"},
    "ana@teste.com": {"perfil": "vendedor", "regiao": "Sul"}
}

usuario_logado = st.session_state.get("usuario", "marco@teste.com")
perfil_logado = usuarios.get(usuario_logado, {}).get("perfil", "vendedor")

if perfil_logado == "admin":
    st.success("👑 Você é um administrador. Pode gerenciar os usuários abaixo.")

    for email, dados in usuarios.items():
        with st.expander(f"📧 {email}"):
            novo_perfil = st.selectbox(f"Perfil de {email}", ["admin", "vendedor"], index=["admin", "vendedor"].index(dados["perfil"]), key=f"perfil_{email}")
            nova_regiao = st.text_input(f"Região de atuação de {email}", value=dados["regiao"], key=f"regiao_{email}")

            if st.button(f"💾 Salvar mudanças para {email}", key=f"save_{email}"):
                usuarios[email]["perfil"] = novo_perfil
                usuarios[email]["regiao"] = nova_regiao
                st.success(f"✅ Alterações salvas para {email}!")
else:
    st.info("🔒 Apenas administradores podem gerenciar usuários.")

st.markdown("</div>", unsafe_allow_html=True)

# 🔌 Integrações futuras
st.markdown("""
    <div class='config-card'>
        <h3>🔌 Integrações</h3>
        <ul>
            <li>📤 Integração com Google Sheets: <em>Em breve</em></li>
            <li>🔑 Gerenciamento de API Key da OpenAI: <em>Em breve</em></li>
            <li>🗂️ Importação automática de planilhas: <em>Em breve</em></li>
            <li>📡 Integração com CRM externo: <em>Em planejamento</em></li>
            <li>📬 Notificações via WhatsApp/Email: <em>Em planejamento</em></li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# 🛠️ Outras Configurações futuras
st.markdown("""
    <div class='config-card'>
        <h3>🛠️ Outras Configurações</h3>
        <p>Esta seção será expandida com opções adicionais conforme a plataforma evolui.</p>
        <ul>
            <li>📈 Preferências de visualização de gráficos</li>
            <li>🗃️ Exportação automática de relatórios</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# pages/8⚙️_Configurações.py
import streamlit as st

st.set_page_config(page_title="⚙️ Configurações", page_icon="🛠️", layout="wide")

from style_config import *

st.markdown("""
    <style>
        .config-card {
            background-color: #f5f5f5;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .config-card h3 {
            margin-bottom: 1rem;
            color: #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("# ⚙️ Configurações")
st.caption("Ajuste suas preferências de sistema, notificações, integrações e permissões de usuário.")

# 🔧 Preferências de Interface
st.markdown("""
    <div class='config-card'>
        <h3>🔧 Preferências de Interface</h3>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    modo_escuro = st.checkbox("🌙 Ativar modo escuro (visual)", value=st.session_state.get("modo_escuro", False))
    notificacoes = st.checkbox("🔔 Receber notificações por email", value=st.session_state.get("notificacoes", False))
with col2:
    linguagem = st.selectbox("🌍 Idioma preferido", ["Português", "Inglês", "Espanhol"], index=["Português", "Inglês", "Espanhol"].index(st.session_state.get("linguagem", "Português")))
    timezone = st.selectbox("🕐 Fuso horário", ["UTC-3 (Brasília)", "UTC-4", "UTC-5"], index=["UTC-3 (Brasília)", "UTC-4", "UTC-5"].index(st.session_state.get("timezone", "UTC-3 (Brasília)")))

st.session_state["modo_escuro"] = modo_escuro
st.session_state["notificacoes"] = notificacoes
st.session_state["linguagem"] = linguagem
st.session_state["timezone"] = timezone

if st.button("💾 Salvar Configurações"):
    st.success("✅ Preferências salvas com sucesso!")

st.markdown("</div>", unsafe_allow_html=True)

# 🔐 Gerenciamento de Usuários e Permissões
st.markdown("""
    <div class='config-card'>
        <h3>👥 Gerenciamento de Usuários e Permissões</h3>
""", unsafe_allow_html=True)

usuarios = {
    "marco@teste.com": {"perfil": "admin", "regiao": "Sul/Sudeste"},
    "joao@teste.com": {"perfil": "vendedor", "regiao": "Sudeste"},
    "ana@teste.com": {"perfil": "vendedor", "regiao": "Sul"}
}

usuario_logado = st.session_state.get("usuario", "marco@teste.com")
perfil_logado = usuarios.get(usuario_logado, {}).get("perfil", "vendedor")

if perfil_logado == "admin":
    st.success("👑 Você é um administrador. Pode gerenciar os usuários abaixo.")

    for email, dados in usuarios.items():
        with st.expander(f"📧 {email}"):
            novo_perfil = st.selectbox(f"Perfil de {email}", ["admin", "vendedor"], index=["admin", "vendedor"].index(dados["perfil"]), key=f"perfil_{email}")
            nova_regiao = st.text_input(f"Região de atuação de {email}", value=dados["regiao"], key=f"regiao_{email}")

            if st.button(f"💾 Salvar mudanças para {email}", key=f"save_{email}"):
                usuarios[email]["perfil"] = novo_perfil
                usuarios[email]["regiao"] = nova_regiao
                st.success(f"✅ Alterações salvas para {email}!")
else:
    st.info("🔒 Apenas administradores podem gerenciar usuários.")

st.markdown("</div>", unsafe_allow_html=True)

# 🔌 Integrações futuras
st.markdown("""
    <div class='config-card'>
        <h3>🔌 Integrações</h3>
        <ul>
            <li>📤 Integração com Google Sheets: <em>Em breve</em></li>
            <li>🔑 Gerenciamento de API Key da OpenAI: <em>Em breve</em></li>
            <li>🗂️ Importação automática de planilhas: <em>Em breve</em></li>
            <li>📡 Integração com CRM externo: <em>Em planejamento</em></li>
            <li>📬 Notificações via WhatsApp/Email: <em>Em planejamento</em></li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# 🛠️ Outras Configurações futuras
st.markdown("""
    <div class='config-card'>
        <h3>🛠️ Outras Configurações</h3>
        <p>Esta seção será expandida com opções adicionais conforme a plataforma evolui.</p>
        <ul>
            <li>📈 Preferências de visualização de gráficos</li>
            <li>🗃️ Exportação automática de relatórios</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

