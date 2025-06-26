<<<<<<< HEAD
import streamlit as st

# 🛠️ Configuração da página
st.set_page_config(page_title="📋 Curva ABC", layout="wide")
st.markdown("# 📋 Curva ABC de Produtos")

import openai
import pandas as pd
import plotly.express as px
from style_config import *

# 🔐 Chave da OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ Chave da OpenAI ausente ou mal configurada.")
    st.stop()

# 🔒 Verificação de dados
if "resumo_df" not in st.session_state or "df_curva" not in st.session_state:
    st.warning("⚠️ Dados ausentes. Importe primeiro na página 'Importar Dados'.")
    st.stop()

resumo_df = st.session_state["resumo_df"]
df_curva = st.session_state["df_curva"]

# 🔄 Merge entre produtos vendidos (resumo) e classificação ABC
produtos_vendidos = resumo_df[["Código", "Descrição"]].drop_duplicates()
produtos_com_curva = produtos_vendidos.merge(df_curva, on="Código", how="left")

# 🌟 Amostra para IA
amostra_curva = produtos_com_curva.head(300).to_string(index=False)

# 🧐 Sugestões e prompt IA
st.markdown("---")
st.subheader("🤖 Pergunte à IA sobre a Curva ABC")

sugestoes = [
    "Quantos produtos estão na classe A?",
    "Qual a distribuição percentual entre A, B e C?",
    "Qual o impacto da classe A no faturamento?",
    "O mix de produtos está equilibrado?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s, key=f"pergunta_{i}"):
        st.session_state["pergunta_curva"] = s

pergunta = st.text_input("Digite uma pergunta sobre a Curva ABC:", value=st.session_state.pop("pergunta_curva", ""))

if pergunta:
    with st.spinner("Analisando com IA..."):
        prompt = f"""
        Você é um vendedor sênior em vendas B2B. Com base na seguinte tabela de classificação ABC (código, descrição, curva):

        {amostra_curva}

        Responda com foco em estratégia de vendas, gerenciamento de estoque e tomada de decisão:
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

# 📊 Gráfico de distribuição ABC
st.markdown("---")
st.subheader("📊 Distribuição ABC dos Produtos Vendidos")
distribuicao = produtos_com_curva["Curva ABC"].value_counts().reset_index()
distribuicao.columns = ["Faixa", "Quantidade"]
distribuicao = distribuicao.sort_values(by="Faixa", key=lambda x: x.map({"A": 0, "B": 1, "C": 2}))
fig = px.pie(distribuicao, names="Faixa", values="Quantidade", title="Distribuição ABC dos Produtos")
st.plotly_chart(fig, use_container_width=True)

# 📋 Tabela com códigos e curva dos vendidos
st.markdown("---")
st.subheader("📋 Classificação ABC dos Produtos Vendidos")
colunas_exibicao = [col for col in ["Código", "Descrição", "Curva ABC"] if col in produtos_com_curva.columns]
st.dataframe(produtos_com_curva[colunas_exibicao].drop_duplicates(), use_container_width=True)
=======
import streamlit as st

# 🛠️ Configuração da página
st.set_page_config(page_title="📋 Curva ABC", layout="wide")
st.markdown("# 📋 Curva ABC de Produtos")

import openai
import pandas as pd
import plotly.express as px
from style_config import *

# 🔐 Chave da OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ Chave da OpenAI ausente ou mal configurada.")
    st.stop()

# 🔒 Verificação de dados
if "resumo_df" not in st.session_state or "df_curva" not in st.session_state:
    st.warning("⚠️ Dados ausentes. Importe primeiro na página 'Importar Dados'.")
    st.stop()

resumo_df = st.session_state["resumo_df"]
df_curva = st.session_state["df_curva"]

# 🔄 Merge entre produtos vendidos (resumo) e classificação ABC
produtos_vendidos = resumo_df[["Código", "Descrição"]].drop_duplicates()
produtos_com_curva = produtos_vendidos.merge(df_curva, on="Código", how="left")

# 🌟 Amostra para IA
amostra_curva = produtos_com_curva.head(300).to_string(index=False)

# 🧐 Sugestões e prompt IA
st.markdown("---")
st.subheader("🤖 Pergunte à IA sobre a Curva ABC")

sugestoes = [
    "Quantos produtos estão na classe A?",
    "Qual a distribuição percentual entre A, B e C?",
    "Qual o impacto da classe A no faturamento?",
    "O mix de produtos está equilibrado?"
]

cols = st.columns(len(sugestoes))
for i, s in enumerate(sugestoes):
    if cols[i].button(s, key=f"pergunta_{i}"):
        st.session_state["pergunta_curva"] = s

pergunta = st.text_input("Digite uma pergunta sobre a Curva ABC:", value=st.session_state.pop("pergunta_curva", ""))

if pergunta:
    with st.spinner("Analisando com IA..."):
        prompt = f"""
        Você é um vendedor sênior em vendas B2B. Com base na seguinte tabela de classificação ABC (código, descrição, curva):

        {amostra_curva}

        Responda com foco em estratégia de vendas, gerenciamento de estoque e tomada de decisão:
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

# 📊 Gráfico de distribuição ABC
st.markdown("---")
st.subheader("📊 Distribuição ABC dos Produtos Vendidos")
distribuicao = produtos_com_curva["Curva ABC"].value_counts().reset_index()
distribuicao.columns = ["Faixa", "Quantidade"]
distribuicao = distribuicao.sort_values(by="Faixa", key=lambda x: x.map({"A": 0, "B": 1, "C": 2}))
fig = px.pie(distribuicao, names="Faixa", values="Quantidade", title="Distribuição ABC dos Produtos")
st.plotly_chart(fig, use_container_width=True)

# 📋 Tabela com códigos e curva dos vendidos
st.markdown("---")
st.subheader("📋 Classificação ABC dos Produtos Vendidos")
colunas_exibicao = [col for col in ["Código", "Descrição", "Curva ABC"] if col in produtos_com_curva.columns]
st.dataframe(produtos_com_curva[colunas_exibicao].drop_duplicates(), use_container_width=True)
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
