
import streamlit as st
st.set_page_config(page_title="📥 Importar Dados", page_icon="📤", layout="wide")

import pandas as pd
from style_config import *
from sellout_generator import gerar_sellout, gerar_resumo_itens

# Função inline para carregar a Curva ABC do Google Sheets
def carregar_curva_abc(secrets):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
    client = gspread.authorize(creds)
    url = "https://docs.google.com/spreadsheets/d/1YXjBruX8jb90HOWy07Ccwn1oC846g_AnNnbyIh3HquU/edit?usp=sharing"
    sheet = client.open_by_url(url).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    return df

# Carrega Curva ABC e armazena no session_state
df_curva = carregar_curva_abc(st.secrets["gcp_service_account"])
st.session_state["df_curva"] = df_curva

st.title("📥 Importar Dados de Vendas")

st.markdown("""
Simule o upload de arquivos Excel para alimentar os dados da plataforma.
Este processo ainda é uma demonstração.
""")

# Upload
arquivo = st.file_uploader("Selecione um arquivo Excel (.xlsx)", type="xlsx")

if arquivo:
    st.success("✅ Arquivo carregado com sucesso!")
    df = pd.read_excel(arquivo)
    df.columns = df.columns.str.strip()

    st.subheader("📄 Prévia dos dados carregados")
    st.dataframe(df.head(), use_container_width=True)

    try:
        sellout_df = gerar_sellout(df)
        resumo_df = gerar_resumo_itens(df)

        st.session_state["sellout_df"] = sellout_df
        st.session_state["resumo_df"] = resumo_df

        st.success("✅ Dados processados e armazenados com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro ao processar os dados: {e}")
else:
    st.warning("Envie um arquivo Excel para simular a importação de dados.")

import streamlit as st
st.set_page_config(page_title="📥 Importar Dados", page_icon="📤", layout="wide")

import pandas as pd
from style_config import *
from sellout_generator import gerar_sellout, gerar_resumo_itens

# Função inline para carregar a Curva ABC do Google Sheets
def carregar_curva_abc(secrets):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
    client = gspread.authorize(creds)
    url = "https://docs.google.com/spreadsheets/d/1YXjBruX8jb90HOWy07Ccwn1oC846g_AnNnbyIh3HquU/edit?usp=sharing"
    sheet = client.open_by_url(url).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    return df

# Carrega Curva ABC e armazena no session_state
df_curva = carregar_curva_abc(st.secrets["gcp_service_account"])
st.session_state["df_curva"] = df_curva

st.title("📥 Importar Dados de Vendas")

st.markdown("""
Simule o upload de arquivos Excel para alimentar os dados da plataforma.
Este processo ainda é uma demonstração.
""")

# Upload
arquivo = st.file_uploader("Selecione um arquivo Excel (.xlsx)", type="xlsx")

if arquivo:
    st.success("✅ Arquivo carregado com sucesso!")
    df = pd.read_excel(arquivo)
    df.columns = df.columns.str.strip()

    st.subheader("📄 Prévia dos dados carregados")
    st.dataframe(df.head(), use_container_width=True)

    try:
        sellout_df = gerar_sellout(df)
        resumo_df = gerar_resumo_itens(df)

        st.session_state["sellout_df"] = sellout_df
        st.session_state["resumo_df"] = resumo_df

        st.success("✅ Dados processados e armazenados com sucesso!")

    except Exception as e:
        st.error(f"❌ Erro ao processar os dados: {e}")
else:
    st.warning("Envie um arquivo Excel para simular a importação de dados.")

