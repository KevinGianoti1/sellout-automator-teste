<<<<<<< HEAD
import streamlit as st
import pandas as pd
from style_config import *

st.set_page_config(page_title="📊 Curva ABC", layout="wide")
st.markdown("# 📊 Curva ABC de Produtos")

# Verifica se os dados foram importados
if "sellout_df" not in st.session_state or "df_curva" not in st.session_state:
    st.warning("⚠️ Faça o upload dos dados primeiro na página 'Importar Dados'.")
    st.stop()

# Dados do session_state
df = st.session_state["sellout_df"]
df_curva = st.session_state["df_curva"]

# Merge com segurança
if "Código" in df.columns and "Código" in df_curva.columns:
    df_merged = df.merge(df_curva[["Código", "Curva ABC"]], on="Código", how="left")
else:
    st.error("❌ Coluna 'Código' ausente em uma das bases.")
    st.stop()

# Verifica se 'Curva ABC' existe após o merge
if "Curva ABC" not in df_merged.columns:
    st.error("❌ A coluna 'Curva ABC' não está presente na base. Verifique a planilha da Curva ABC.")
    st.write("🔍 Colunas atuais no dataframe:", df_merged.columns.tolist())
    st.stop()

# Tabela com contagem de produtos por faixa
distribuicao = df_merged["Curva ABC"].value_counts().reset_index()
distribuicao.columns = ["Faixa", "Quantidade"]

# Gráfico de pizza
import plotly.express as px
fig = px.pie(distribuicao, names="Faixa", values="Quantidade", title="Distribuição ABC dos Produtos")
st.plotly_chart(fig, use_container_width=True)

# Exibição da Tabela
st.subheader("📦 Tabela com Classificação ABC")
st.dataframe(df_merged[["Código", "Descrição", "Curva ABC"]].drop_duplicates(), use_container_width=True)
=======
import streamlit as st
import pandas as pd
from style_config import *

st.set_page_config(page_title="📊 Curva ABC", layout="wide")
st.markdown("# 📊 Curva ABC de Produtos")

# Verifica se os dados foram importados
if "sellout_df" not in st.session_state or "df_curva" not in st.session_state:
    st.warning("⚠️ Faça o upload dos dados primeiro na página 'Importar Dados'.")
    st.stop()

# Dados do session_state
df = st.session_state["sellout_df"]
df_curva = st.session_state["df_curva"]

# Merge com segurança
if "Código" in df.columns and "Código" in df_curva.columns:
    df_merged = df.merge(df_curva[["Código", "Curva ABC"]], on="Código", how="left")
else:
    st.error("❌ Coluna 'Código' ausente em uma das bases.")
    st.stop()

# Verifica se 'Curva ABC' existe após o merge
if "Curva ABC" not in df_merged.columns:
    st.error("❌ A coluna 'Curva ABC' não está presente na base. Verifique a planilha da Curva ABC.")
    st.write("🔍 Colunas atuais no dataframe:", df_merged.columns.tolist())
    st.stop()

# Tabela com contagem de produtos por faixa
distribuicao = df_merged["Curva ABC"].value_counts().reset_index()
distribuicao.columns = ["Faixa", "Quantidade"]

# Gráfico de pizza
import plotly.express as px
fig = px.pie(distribuicao, names="Faixa", values="Quantidade", title="Distribuição ABC dos Produtos")
st.plotly_chart(fig, use_container_width=True)

# Exibição da Tabela
st.subheader("📦 Tabela com Classificação ABC")
st.dataframe(df_merged[["Código", "Descrição", "Curva ABC"]].drop_duplicates(), use_container_width=True)
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
