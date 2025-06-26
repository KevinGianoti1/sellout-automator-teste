<<<<<<< HEAD
import streamlit as st
from style_config import *
from db import buscar_sellout
from sellout_generator import plotar_grafico_sellout

st.set_page_config(page_title="📊 Dashboard", page_icon="📈", layout="wide")
st.markdown("# 📊 Dashboard de Vendas")

# 🔻 Recupera dados salvos
usuario = st.session_state.get("usuario", "Anonimo")
sellout_df = buscar_sellout(usuario)

if sellout_df.empty:
    st.warning("Nenhum dado encontrado. Importe um arquivo na aba 'Importar Dados'.")
    st.stop()

# 🎯 KPIs
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

st.markdown("---")

# 📊 Gráfico
st.subheader("Evolução de Vendas")
fig = plotar_grafico_sellout(sellout_df)
st.plotly_chart(fig, use_container_width=True)

# 📅 Dados tabulares
with st.expander("📋 Visualizar Dados Tabulares"):
    st.dataframe(sellout_df, use_container_width=True)
=======
import streamlit as st
from style_config import *
from db import buscar_sellout
from sellout_generator import plotar_grafico_sellout

st.set_page_config(page_title="📊 Dashboard", page_icon="📈", layout="wide")
st.markdown("# 📊 Dashboard de Vendas")

# 🔻 Recupera dados salvos
usuario = st.session_state.get("usuario", "Anonimo")
sellout_df = buscar_sellout(usuario)

if sellout_df.empty:
    st.warning("Nenhum dado encontrado. Importe um arquivo na aba 'Importar Dados'.")
    st.stop()

# 🎯 KPIs
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

st.markdown("---")

# 📊 Gráfico
st.subheader("Evolução de Vendas")
fig = plotar_grafico_sellout(sellout_df)
st.plotly_chart(fig, use_container_width=True)

# 📅 Dados tabulares
with st.expander("📋 Visualizar Dados Tabulares"):
    st.dataframe(sellout_df, use_container_width=True)
>>>>>>> ac43d95327d7b538c41408063131c50a1c5b6699
