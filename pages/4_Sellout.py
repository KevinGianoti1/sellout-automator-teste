import streamlit as st
import pandas as pd
from db import buscar_sellout, buscar_resumo
from style_config import *

st.set_page_config(page_title="📦 Sell Out", page_icon="📊", layout="wide")
st.markdown("# 📦 Análise Sell Out")

# 🔐 Validação de estado
if "sellout_df" not in st.session_state or "resumo_df" not in st.session_state:
    st.warning("⚠️ Faça o upload dos dados primeiro na página 'Importar Dados'.")
    st.stop()

sellout_df = st.session_state["sellout_df"]
resumo_df = st.session_state["resumo_df"]

# 📊 Tabela 1 - Totais por Ano e Mês
total_mensal = sellout_df.melt(id_vars=["Cliente", "Ano"], var_name="Mês", value_name="Total")
total_mensal = total_mensal.groupby(["Ano", "Mês"]).agg({"Total": "sum"}).reset_index()

st.subheader("📅 Totais por Mês")
st.dataframe(total_mensal, use_container_width=True)

# 📦 Tabela 2 - Resumo SKU
st.subheader("📦 Detalhes por SKU")
st.dataframe(resumo_df, use_container_width=True)

# 📁 Download das tabelas
with st.expander("⬇️ Exportar Dados"):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📁 Exportar Sellout", data=sellout_df.to_csv(index=False).encode("utf-8"), file_name="sellout.csv", mime="text/csv")
    with col2:
        st.download_button("📁 Exportar Resumo", data=resumo_df.to_csv(index=False).encode("utf-8"), file_name="resumo.csv", mime="text/csv")
