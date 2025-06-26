
import streamlit as st
import pandas as pd
import plotly.express as px
from style_config import *

# 🤿 Configuração
st.set_page_config(page_title="👤 Perfil do Cliente", page_icon="💼", layout="wide")
st.markdown("""
    <style>
    .perfil-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .perfil-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .info-label {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='perfil-header'>👤 Perfil do Cliente</div>", unsafe_allow_html=True)

# 🤖 Dados simulados
cliente = st.session_state.get("cliente", "Loja Exemplo")
regiao = st.session_state.get("regiao", "Sudeste")
responsavel = st.session_state.get("usuario", "marco@teste.com")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        <div class='perfil-card'>
        <p><span class='info-label'>Cliente:</span> {}</p>
        <p><span class='info-label'>Região:</span> {}</p>
        <p><span class='info-label'>Responsável:</span> {}</p>
        </div>
    """.format(cliente, regiao, responsavel), unsafe_allow_html=True)

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=160)

# 📆 Seletor de Período
st.markdown("---")
st.subheader("📊 Análise de Compras por Período")

df = st.session_state.get("sellout_df")

if df is not None and "Ano" in df.columns:
    ano = st.selectbox("Selecione o ano:", sorted(df["Ano"].unique(), reverse=True))
    df_periodo = df[df["Ano"] == ano]

    df_total = df_periodo.iloc[:, 2:].sum().reset_index()
    df_total.columns = ["Mês", "Total"]
    df_total = df_total.sort_values(by="Mês")

    fig = px.line(df_total, x="Mês", y="Total", title=f"Evolução de Compras - {ano}", markers=True)
    fig.update_traces(texttemplate="R$ %{y:,.2f}", hovertemplate="Mês: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Ver Tabela de Compras"):
        st.dataframe(df_total, use_container_width=True)
else:
    st.warning("Nenhum dado de venda encontrado.")
