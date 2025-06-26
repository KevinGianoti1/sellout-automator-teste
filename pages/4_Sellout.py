<<<<<<< HEAD
import streamlit as st

# 🔧 Configuração da página
st.set_page_config(page_title="📦 Sell Out", page_icon="📊", layout="wide")
st.markdown("# 📦 Análise Sell Out")

import openai
import pandas as pd
from style_config import *
from db import buscar_sellout, buscar_resumo
from sellout_generator import plotar_grafico_sellout

# 🔑 Configura API OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ A chave da OpenAI não foi configurada corretamente.")
    st.stop()

# 🔐 Verificação de dados
if "sellout_df" not in st.session_state or "resumo_df" not in st.session_state:
    st.warning("⚠️ Faça o upload dos dados primeiro na página 'Importar Dados'.")
    st.stop()

sellout_df = st.session_state["sellout_df"]
resumo_df = st.session_state["resumo_df"]

# 🤖 Assistente de IA
st.markdown("---")
st.subheader("🤖 Insights de Sell Out com IA")

sugestoes = [
    "Qual SKU teve maior volume vendido?",
    "Qual SKU que comprou no melhor mês?",
    "Qual foi a média de preço por cliente?",
    "Quais produtos tiveram queda nas vendas?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s):
        st.session_state["pergunta_sellout"] = s

pergunta = st.text_input("Pergunta sobre os dados de Sell Out:", value=st.session_state.get("pergunta_sellout", ""))

if pergunta:
    with st.spinner("Consultando GPT-4o..."):
        contexto = resumo_df.head(1000).to_string(index=False)
        prompt = f"""
        Você é um vendedor sênior em vendas B2B. Com base no seguinte resumo de dados (SKU, descrição, quantidade, valor, preço):

        {contexto}

        Responda a pergunta a seguir de forma prática e voltada à tomada de decisão em vendas:
        {pergunta}
        """

        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        conteudo = resposta.choices[0].message.content
        st.success("💡 Resposta da IA:")
        st.markdown(f"> {conteudo}")

# 🎯 Filtros interativos
anos = sorted(sellout_df["Ano"].unique())
clientes = sorted(sellout_df["Cliente"].unique())

col_f1, col_f2 = st.columns(2)
with col_f1:
    ano_sel = st.selectbox("Filtrar por Ano", options=["Todos"] + anos)
with col_f2:
    cliente_sel = st.selectbox("Filtrar por Cliente", options=["Todos"] + clientes)

filtro_df = sellout_df.copy()
if ano_sel != "Todos":
    filtro_df = filtro_df[filtro_df["Ano"] == ano_sel]
if cliente_sel != "Todos":
    filtro_df = filtro_df[filtro_df["Cliente"] == cliente_sel]

# 📊 Tabela - Totais por Ano e Mês
st.markdown("---")
st.subheader("📅 Totais Mensais por Ano")
total_mensal = filtro_df.melt(id_vars=["Cliente", "Ano"], var_name="Mês", value_name="Total")
total_mensal = total_mensal.groupby(["Ano", "Mês"]).agg({"Total": "sum"}).reset_index()
st.dataframe(total_mensal, use_container_width=True)

# 📦 Tabela - Resumo de Itens
st.markdown("---")
st.subheader("📦 Resumo de SKUs Vendidos")
st.dataframe(resumo_df, use_container_width=True)

# 📁 Botões de Download
with st.expander("⬇️ Exportar Relatórios"):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📁 Baixar Sell Out", data=sellout_df.to_csv(index=False).encode("utf-8"), file_name="sellout.csv", mime="text/csv")
    with col2:
        st.download_button("📁 Baixar Resumo de Itens", data=resumo_df.to_csv(index=False).encode("utf-8"), file_name="resumo.csv", mime="text/csv")
=======
import streamlit as st

# 🔧 Configuração da página
st.set_page_config(page_title="📦 Sell Out", page_icon="📊", layout="wide")
st.markdown("# 📦 Análise Sell Out")

import openai
import pandas as pd
from style_config import *
from db import buscar_sellout, buscar_resumo
from sellout_generator import plotar_grafico_sellout

# 🔑 Configura API OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ A chave da OpenAI não foi configurada corretamente.")
    st.stop()

# 🔐 Verificação de dados
if "sellout_df" not in st.session_state or "resumo_df" not in st.session_state:
    st.warning("⚠️ Faça o upload dos dados primeiro na página 'Importar Dados'.")
    st.stop()

sellout_df = st.session_state["sellout_df"]
resumo_df = st.session_state["resumo_df"]

# 🤖 Assistente de IA
st.markdown("---")
st.subheader("🤖 Insights de Sell Out com IA")

sugestoes = [
    "Qual SKU teve maior volume vendido?",
    "Qual SKU que comprou no melhor mês?",
    "Qual foi a média de preço por cliente?",
    "Quais produtos tiveram queda nas vendas?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s):
        st.session_state["pergunta_sellout"] = s

pergunta = st.text_input("Pergunta sobre os dados de Sell Out:", value=st.session_state.get("pergunta_sellout", ""))

if pergunta:
    with st.spinner("Consultando GPT-4o..."):
        contexto = resumo_df.head(1000).to_string(index=False)
        prompt = f"""
        Você é um vendedor sênior em vendas B2B. Com base no seguinte resumo de dados (SKU, descrição, quantidade, valor, preço):

        {contexto}

        Responda a pergunta a seguir de forma prática e voltada à tomada de decisão em vendas:
        {pergunta}
        """

        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        conteudo = resposta.choices[0].message.content
        st.success("💡 Resposta da IA:")
        st.markdown(f"> {conteudo}")

# 🎯 Filtros interativos
anos = sorted(sellout_df["Ano"].unique())
clientes = sorted(sellout_df["Cliente"].unique())

col_f1, col_f2 = st.columns(2)
with col_f1:
    ano_sel = st.selectbox("Filtrar por Ano", options=["Todos"] + anos)
with col_f2:
    cliente_sel = st.selectbox("Filtrar por Cliente", options=["Todos"] + clientes)

filtro_df = sellout_df.copy()
if ano_sel != "Todos":
    filtro_df = filtro_df[filtro_df["Ano"] == ano_sel]
if cliente_sel != "Todos":
    filtro_df = filtro_df[filtro_df["Cliente"] == cliente_sel]

# 📊 Tabela - Totais por Ano e Mês
st.markdown("---")
st.subheader("📅 Totais Mensais por Ano")
total_mensal = filtro_df.melt(id_vars=["Cliente", "Ano"], var_name="Mês", value_name="Total")
total_mensal = total_mensal.groupby(["Ano", "Mês"]).agg({"Total": "sum"}).reset_index()
st.dataframe(total_mensal, use_container_width=True)

# 📦 Tabela - Resumo de Itens
st.markdown("---")
st.subheader("📦 Resumo de SKUs Vendidos")
st.dataframe(resumo_df, use_container_width=True)

# 📁 Botões de Download
with st.expander("⬇️ Exportar Relatórios"):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📁 Baixar Sell Out", data=sellout_df.to_csv(index=False).encode("utf-8"), file_name="sellout.csv", mime="text/csv")
    with col2:
        st.download_button("📁 Baixar Resumo de Itens", data=resumo_df.to_csv(index=False).encode("utf-8"), file_name="resumo.csv", mime="text/csv")
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
