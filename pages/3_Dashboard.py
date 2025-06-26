
import streamlit as st

# 🔧 Configuração da página
st.set_page_config(page_title="📊 Dashboard", page_icon="📈", layout="wide")
st.markdown("# 📊 Dashboard de Vendas")

import openai
import pandas as pd
from style_config import *
from db import buscar_sellout
from sellout_generator import plotar_grafico_sellout

# 🔑 Configura API OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ A chave da OpenAI não foi configurada corretamente.")
    st.stop()

# 🔻 Recupera dados salvos
usuario = st.session_state.get("usuario", "Anonimo")
sellout_df = st.session_state.get("sellout_df")

if sellout_df is None:
    st.warning("Nenhum dado encontrado. Importe um arquivo na aba 'Importar Dados'.")
    st.stop()

# 🤖 Assistente de IA
st.markdown("---")
st.subheader("🤖 Insights Inteligentes para Vendas B2B")

sugestoes = [
    "Qual a porcentagem de cada mês no melhor mês de compras?",
    "Quais meses apresentam maior volume de vendas?",
    "Existe sazonalidade nas vendas por cliente?",
    "Qual o ticket médio por cliente este ano?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s):
        st.session_state["pergunta"] = s

pergunta = st.text_input("Digite sua pergunta sobre os dados de vendas:", value=st.session_state.get("pergunta", ""))

if pergunta:
    with st.spinner("Consultando GPT-4o..."):
        contexto = sellout_df.head(1000).to_string(index=False)
        prompt = f"""
        Você é um vendedor sênior B2B. Com base na amostra de dados a seguir, forneça insights que possam ajudar um time de vendas a agir estrategicamente:

        {contexto}

        Pergunta:
        {pergunta}

        Seja claro, direto e use uma linguagem prática para vendedores. Forneça sugestões ou observações aplicáveis quando possível.
        """

        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        conteudo = resposta.choices[0].message.content
        st.success("💡 Resposta da IA:")
        st.markdown(f"> {conteudo}")

# 📌 KPIs
st.markdown("---")
st.subheader("📌 Indicadores de Desempenho")
col1, col2, col3 = st.columns(3)
with col1:
    total = sellout_df.iloc[:, 2:].sum().sum()
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Comprado</div><div class='kpi-value'>R$ {total:,.2f}</div></div>", unsafe_allow_html=True)

with col2:
    ticket = total / sellout_df.shape[0] if sellout_df.shape[0] > 0 else 0
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Ticket Médio</div><div class='kpi-value'>R$ {ticket:,.2f}</div></div>", unsafe_allow_html=True)

with col3:
    clientes = sellout_df["Cliente"].nunique()
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Clientes Únicos</div><div class='kpi-value'>{clientes}</div></div>", unsafe_allow_html=True)

# 📈 Gráfico
st.markdown("---")
st.subheader("📈 Evolução de Vendas")
fig = plotar_grafico_sellout(sellout_df)
st.plotly_chart(fig, use_container_width=True)

# 📋 Tabela
st.markdown("---")
st.subheader("📋 Tabela SellOut")
st.dataframe(sellout_df, use_container_width=True)

import streamlit as st

# 🔧 Configuração da página
st.set_page_config(page_title="📊 Dashboard", page_icon="📈", layout="wide")
st.markdown("# 📊 Dashboard de Vendas")

import openai
import pandas as pd
from style_config import *
from db import buscar_sellout
from sellout_generator import plotar_grafico_sellout

# 🔑 Configura API OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ A chave da OpenAI não foi configurada corretamente.")
    st.stop()

# 🔻 Recupera dados salvos
usuario = st.session_state.get("usuario", "Anonimo")
sellout_df = st.session_state.get("sellout_df")

if sellout_df is None:
    st.warning("Nenhum dado encontrado. Importe um arquivo na aba 'Importar Dados'.")
    st.stop()

# 🤖 Assistente de IA
st.markdown("---")
st.subheader("🤖 Insights Inteligentes para Vendas B2B")

sugestoes = [
    "Qual a porcentagem de cada mês no melhor mês de compras?",
    "Quais meses apresentam maior volume de vendas?",
    "Existe sazonalidade nas vendas por cliente?",
    "Qual o ticket médio por cliente este ano?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s):
        st.session_state["pergunta"] = s

pergunta = st.text_input("Digite sua pergunta sobre os dados de vendas:", value=st.session_state.get("pergunta", ""))

if pergunta:
    with st.spinner("Consultando GPT-4o..."):
        contexto = sellout_df.head(1000).to_string(index=False)
        prompt = f"""
        Você é um vendedor sênior B2B. Com base na amostra de dados a seguir, forneça insights que possam ajudar um time de vendas a agir estrategicamente:

        {contexto}

        Pergunta:
        {pergunta}

        Seja claro, direto e use uma linguagem prática para vendedores. Forneça sugestões ou observações aplicáveis quando possível.
        """

        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        conteudo = resposta.choices[0].message.content
        st.success("💡 Resposta da IA:")
        st.markdown(f"> {conteudo}")

# 📌 KPIs
st.markdown("---")
st.subheader("📌 Indicadores de Desempenho")
col1, col2, col3 = st.columns(3)
with col1:
    total = sellout_df.iloc[:, 2:].sum().sum()
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Comprado</div><div class='kpi-value'>R$ {total:,.2f}</div></div>", unsafe_allow_html=True)

with col2:
    ticket = total / sellout_df.shape[0] if sellout_df.shape[0] > 0 else 0
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Ticket Médio</div><div class='kpi-value'>R$ {ticket:,.2f}</div></div>", unsafe_allow_html=True)

with col3:
    clientes = sellout_df["Cliente"].nunique()
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Clientes Únicos</div><div class='kpi-value'>{clientes}</div></div>", unsafe_allow_html=True)

# 📈 Gráfico
st.markdown("---")
st.subheader("📈 Evolução de Vendas")
fig = plotar_grafico_sellout(sellout_df)
st.plotly_chart(fig, use_container_width=True)

# 📋 Tabela
st.markdown("---")
st.subheader("📋 Tabela SellOut")
st.dataframe(sellout_df, use_container_width=True)

