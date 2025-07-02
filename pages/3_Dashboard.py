
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
        Você é um analista comercial experiente em vendas B2B, com foco em geração de insights estratégicos.

        Abaixo está uma amostra dos dados de Sell Out (vendas por cliente, ano, mês e valores totais). Com base nesses dados, responda à pergunta com uma análise clara, prática e orientada à tomada de decisão.

        ### Dados de vendas:
        {contexto}

        ### Pergunta:
        {pergunta}

        ### Instruções para a resposta:
        - Use linguagem comercial acessível a times de vendas.
        - Se possível, traga porcentagens, comparações e padrões de comportamento.
        - Aponte tendências de crescimento, sazonalidade ou concentração de vendas.
        - Utilize listas ou estruturações visuais para facilitar leitura.
        - Dê sugestões de ação (ex: “focar campanhas no mês X”, “negociar com cliente Y”, etc).
        - Evite rodeios e contextualizações desnecessárias.

        Se os dados forem insuficientes, diga isso com transparência.
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

# Filtro de Ano
anos_disponiveis = sorted(sellout_df["Ano"].unique(), reverse=True)
ano_selecionado = st.selectbox("Selecione o Ano", options=["Todos"] + anos_disponiveis)

# Aplica filtro no gráfico
if ano_selecionado == "Todos":
    fig = plotar_grafico_sellout(sellout_df)
else:
    fig = plotar_grafico_sellout(sellout_df, ano=int(ano_selecionado))

st.plotly_chart(fig, use_container_width=True)

# 📋 Tabela SellOut com Filtros, R$ e Total por Linha
st.markdown("---")
st.subheader("📋 Tabela SellOut")

# Filtros interativos
col1, col2 = st.columns(2)
anos = sorted(sellout_df["Ano"].unique(), reverse=True)
clientes = sorted(sellout_df["Cliente"].unique())

with col1:
    ano_filtro = st.selectbox("Filtrar por Ano", options=["Todos"] + anos)
with col2:
    cliente_filtro = st.selectbox("Filtrar por Cliente", options=["Todos"] + clientes)

filtro = sellout_df.copy()
if ano_filtro != "Todos":
    filtro = filtro[filtro["Ano"] == ano_filtro]
if cliente_filtro != "Todos":
    filtro = filtro[filtro["Cliente"] == cliente_filtro]

# Detecta colunas monetárias (exceto "Ano")
colunas_valores = filtro.select_dtypes(include=["float", "int"]).columns.tolist()
colunas_valores = [col for col in colunas_valores if col != "Ano"]

# Tabela formatada
filtro_formatado = filtro.copy()
filtro_formatado[colunas_valores] = filtro_formatado[colunas_valores].applymap(
    lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
)

# Calcula totais (linha inferior)
soma_totais = filtro[colunas_valores].sum().to_dict()
linha_total = {col: "" for col in filtro.columns}
linha_total["Cliente"] = "TOTAL GERAL"
for col, valor in soma_totais.items():
    linha_total[col] = f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

df_exibicao = pd.concat(
    [filtro_formatado, pd.DataFrame([linha_total])],
    ignore_index=True
)

st.dataframe(df_exibicao, use_container_width=True)
