import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🏠 Início", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
        .welcome {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
        }
        .subtext {
            font-size: 1.2rem;
            color: #555;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="welcome">Bem-vindo ao SellOut Automator v2</div>
    <div class="subtext">Seu dashboard inteligente de vendas B2B</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/1828/1828817.png", width=200)

with col2:
    st.markdown("""
        ### Funcionalidades principais:
        - Visualização interativa de dados de vendas
        - Análises por SKU, cliente, vendedor e período
        - Classificação ABC de produtos
        - Exportação de relatórios
        - Interface responsiva e amigável
    """)

    st.success("Hoje é: {}".format(datetime.today().strftime("%d/%m/%Y")))

st.markdown("---")

st.info("Use o menu lateral para navegar entre as páginas.")
