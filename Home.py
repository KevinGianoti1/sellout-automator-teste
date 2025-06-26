
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🏠 Início", page_icon="🏠", layout="wide")

# 💅 Estilo customizado
st.markdown("""
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.4rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .feature-list li {
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# 🏠 Título e Subtítulo
st.markdown("""
    <div class="main-title">Bem-vindo ao SellOut Automator v2 🚀</div>
    <div class="subtitle">Seu copiloto inteligente para análise de vendas B2B</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 📊 Painel de introdução
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/5712/5712418.png", width=220)

with col2:
    st.markdown("""
        <h4>Funcionalidades principais:</h4>
        <ul class="feature-list">
            <li>📈 Visualização interativa de dados de vendas</li>
            <li>🔍 Análises por SKU, cliente, vendedor e período</li>
            <li>🏷️ Classificação ABC de produtos</li>
            <li>📁 Exportação de relatórios em Excel</li>
            <li>💬 Integração com IA para insights estratégicos</li>
            <li>🖥️ Interface moderna e responsiva</li>
        </ul>
    """, unsafe_allow_html=True)

    st.success(f"Hoje é: {datetime.today().strftime('%d/%m/%Y')}")

st.markdown("---")

st.info("👈 Use o menu lateral para navegar entre as páginas do seu dashboard.")
=======
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🏠 Início", page_icon="🏠", layout="wide")

# 💅 Estilo customizado
st.markdown("""
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.4rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .feature-list li {
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# 🏠 Título e Subtítulo
st.markdown("""
    <div class="main-title">Bem-vindo ao SellOut Automator v2 🚀</div>
    <div class="subtitle">Seu copiloto inteligente para análise de vendas B2B</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 📊 Painel de introdução
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/5712/5712418.png", width=220)

with col2:
    st.markdown("""
        <h4>Funcionalidades principais:</h4>
        <ul class="feature-list">
            <li>📈 Visualização interativa de dados de vendas</li>
            <li>🔍 Análises por SKU, cliente, vendedor e período</li>
            <li>🏷️ Classificação ABC de produtos</li>
            <li>📁 Exportação de relatórios em Excel</li>
            <li>💬 Integração com IA para insights estratégicos</li>
            <li>🖥️ Interface moderna e responsiva</li>
        </ul>
    """, unsafe_allow_html=True)

    st.success(f"Hoje é: {datetime.today().strftime('%d/%m/%Y')}")

st.markdown("---")

st.info("👈 Use o menu lateral para navegar entre as páginas do seu dashboard.")

