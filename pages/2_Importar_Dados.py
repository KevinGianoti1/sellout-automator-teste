import streamlit as st
import pandas as pd
from style_config import *

st.set_page_config(page_title="📥 Importar Dados", page_icon="📤", layout="wide")

st.title("📥 Importar Dados de Vendas")

st.markdown("""
Simule o upload de arquivos Excel para alimentar os dados da plataforma.
Este processo ainda é uma demonstração.
""")

sellout_df = pd.DataFrame({
    "Ano": [2023, 2023, 2024, 2024],
    "Mês": ["Jan", "Fev", "Jan", "Fev"],
    "Total": [10000, 12000, 14000, 13000]
})

st.session_state["sellout_df"] = sellout_df

arquivo = st.file_uploader("Selecione um arquivo Excel (.xlsx)", type="xlsx")

if arquivo:
    st.success("✅ Arquivo carregado com sucesso!")
    df = pd.read_excel(arquivo)
    df.columns = df.columns.str.strip()
    st.subheader("📄 Prévia dos dados carregados")
    st.dataframe(df.head(), use_container_width=True)

    st.info("Estes dados ainda não são salvos permanentemente. Na versão futura, este upload alimentará o banco de dados.")
else:
    st.warning("Envie um arquivo Excel para simular a importação de dados.")
    st.session_state["sellout_df"] = sellout_df
    st.session_state["resumo_df"] = resumo_df
