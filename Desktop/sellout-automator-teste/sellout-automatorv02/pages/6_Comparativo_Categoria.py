import streamlit as st
import pandas as pd
import plotly.express as px
from db import buscar_resumo
from style_config import *

st.set_page_config(page_title="📊 Comparativo por Categoria", page_icon="📦", layout="wide")
st.markdown("# 🏷️ Comparativo por Categoria")

# Usuário atual
usuario = st.session_state.get("usuario", "Marco (modo dev)")

# Dados
resumo_df = buscar_resumo(usuario)

if resumo_df.empty:
    st.warning("Nenhum dado encontrado. Importe os dados primeiro.")
    st.stop()

# Agrupamento fictício por categoria (simula que 'Descrição' tem categoria)
# No mundo real, você pode extrair isso de um campo como 'Categoria'
resumo_df["Categoria"] = resumo_df["Descricao"].apply(lambda x: x.split()[0])

categoria_df = resumo_df.groupby(["Ano", "Categoria"]).agg({
    "Qtde_Total": "sum",
    "Valor_Total": lambda x: pd.to_numeric(x, errors="coerce").sum()
}).reset_index()

# Filtro por ano
anos = categoria_df["Ano"].unique().tolist()
ano_selecionado = st.selectbox("Ano para Comparativo", sorted(anos, reverse=True))

df_filtrado = categoria_df[categoria_df["Ano"] == ano_selecionado]

# Gráfico
fig = px.bar(
    df_filtrado,
    x="Categoria",
    y="Valor_Total",
    color="Categoria",
    title=f"Comparativo de Vendas por Categoria - {ano_selecionado}",
    text_auto='.2s'
)

fig.update_layout(
    xaxis_title="Categoria",
    yaxis_title="Valor em R$",
    plot_bgcolor="#f9f9f9",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Tabela abaixo
with st.expander("🔎 Ver Tabela Detalhada"):
    st.dataframe(df_filtrado, use_container_width=True)
