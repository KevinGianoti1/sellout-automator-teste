<<<<<<< HEAD
import streamlit as st

# 💧 Configuração
st.set_page_config(page_title="📊 Comparativo por Categoria", page_icon="🛆", layout="wide")
st.markdown("# 🍿️ Comparativo de Categorias com IA")

import pandas as pd
import plotly.express as px
import openai
import json
from db import buscar_resumo
from style_config import *

# 🚀 Chave OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ Chave da OpenAI ausente ou mal configurada.")
    st.stop()

# 📅 Usuário atual e dados
if "resumo_df" not in st.session_state:
    st.warning("Nenhum dado encontrado. Importe os dados primeiro na página 'Importar Dados'.")
    st.stop()

resumo_df = st.session_state["resumo_df"]

# 🔍 Gera categorias via IA a partir das descrições (top 1000)
st.subheader("🧐 Geração de Categorias por IA")
amostra = resumo_df[["Descrição"]].drop_duplicates().head(1000)
descricoes = "; ".join(amostra["Descrição"].astype(str).tolist())

prompt = f"""
Você é um classificador de produtos B2B. Com base nas descrições abaixo, crie uma categoria resumida para cada uma:

{descricoes}

Retorne em formato JSON no estilo:
[
  {{"Descrição": "...", "Categoria": "..."}},
  ...
]
"""

with st.spinner("Gerando categorias via IA..."):
    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = resposta.choices[0].message.content.strip()
        categorias = json.loads(content)
        cat_df = pd.DataFrame(categorias)
        resumo_df = resumo_df.merge(cat_df, on="Descrição", how="left")
        st.success("✅ Categorias geradas com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao processar categorias: {e}")
        st.stop()

# 📈 Comparativo por categoria
st.markdown("---")
st.subheader("📊 Vendas por Categoria")

resumo_df["Valor_Total"] = pd.to_numeric(resumo_df["Valor_Total"], errors="coerce")
categoria_df = resumo_df.groupby(["Ano", "Categoria"]).agg({
    "Qtde_Total": "sum",
    "Valor_Total": "sum"
}).reset_index()

ano_sel = st.selectbox("Ano para Comparativo", sorted(categoria_df["Ano"].unique(), reverse=True))
df_filtrado = categoria_df[categoria_df["Ano"] == ano_sel]

fig = px.bar(
    df_filtrado,
    x="Categoria",
    y="Valor_Total",
    color="Categoria",
    title=f"Comparativo de Vendas por Categoria - {ano_sel}",
    text_auto='.2s'
)
fig.update_layout(xaxis_title="Categoria", yaxis_title="Valor em R$", plot_bgcolor="#f9f9f9", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# 🔢 Tabela Detalhada
with st.expander("🔎 Ver Tabela Detalhada"):
    st.dataframe(df_filtrado, use_container_width=True)
=======
import streamlit as st

# 💧 Configuração
st.set_page_config(page_title="📊 Comparativo por Categoria", page_icon="🛆", layout="wide")
st.markdown("# 🍿️ Comparativo de Categorias com IA")

import pandas as pd
import plotly.express as px
import openai
import json
from db import buscar_resumo
from style_config import *

# 🚀 Chave OpenAI
try:
    openai.api_key = st.secrets["openai"]["key"]
except Exception:
    st.error("❌ Chave da OpenAI ausente ou mal configurada.")
    st.stop()

# 📅 Usuário atual e dados
if "resumo_df" not in st.session_state:
    st.warning("Nenhum dado encontrado. Importe os dados primeiro na página 'Importar Dados'.")
    st.stop()

resumo_df = st.session_state["resumo_df"]

# 🔍 Gera categorias via IA a partir das descrições (top 1000)
st.subheader("🧐 Geração de Categorias por IA")
amostra = resumo_df[["Descrição"]].drop_duplicates().head(1000)
descricoes = "; ".join(amostra["Descrição"].astype(str).tolist())

prompt = f"""
Você é um classificador de produtos B2B. Com base nas descrições abaixo, crie uma categoria resumida para cada uma:

{descricoes}

Retorne em formato JSON no estilo:
[
  {{"Descrição": "...", "Categoria": "..."}},
  ...
]
"""

with st.spinner("Gerando categorias via IA..."):
    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = resposta.choices[0].message.content.strip()
        categorias = json.loads(content)
        cat_df = pd.DataFrame(categorias)
        resumo_df = resumo_df.merge(cat_df, on="Descrição", how="left")
        st.success("✅ Categorias geradas com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao processar categorias: {e}")
        st.stop()

# 📈 Comparativo por categoria
st.markdown("---")
st.subheader("📊 Vendas por Categoria")

resumo_df["Valor_Total"] = pd.to_numeric(resumo_df["Valor_Total"], errors="coerce")
categoria_df = resumo_df.groupby(["Ano", "Categoria"]).agg({
    "Qtde_Total": "sum",
    "Valor_Total": "sum"
}).reset_index()

ano_sel = st.selectbox("Ano para Comparativo", sorted(categoria_df["Ano"].unique(), reverse=True))
df_filtrado = categoria_df[categoria_df["Ano"] == ano_sel]

fig = px.bar(
    df_filtrado,
    x="Categoria",
    y="Valor_Total",
    color="Categoria",
    title=f"Comparativo de Vendas por Categoria - {ano_sel}",
    text_auto='.2s'
)
fig.update_layout(xaxis_title="Categoria", yaxis_title="Valor em R$", plot_bgcolor="#f9f9f9", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# 🔢 Tabela Detalhada
with st.expander("🔎 Ver Tabela Detalhada"):
    st.dataframe(df_filtrado, use_container_width=True)
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
