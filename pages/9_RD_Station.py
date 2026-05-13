import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import db
import plotly.express as px
import plotly.graph_objects as go
from scripts.relatorio_rd_station import gerar_relatorio_excel, gerar_email_html
import os

st.set_page_config(
    page_title="RD Station - Leads",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RD Station - Monitoramento de Leads")

# Criar tabelas se não existirem
try:
    db.criar_tabelas_rd_station()
except Exception as e:
    st.warning(f"Tabelas já existem ou erro ao criar: {str(e)}")

# Sessão de state para refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# ===== BARRA LATERAL - CONFIGURAÇÕES =====
with st.sidebar:
    st.header("⚙️ Configurações")

    st.subheader("API do RD Station")
    api_key = st.text_input(
        "API Key do RD Station",
        type="password",
        help="Insira sua chave de API do RD Station"
    )

    st.subheader("Email para Relatório")
    email_destino = st.text_input(
        "Email destinatário",
        value="analista.vendas@mfferramentas.com.br",
        help="Email que receberá os relatórios diários"
    )

    st.subheader("Configurações de Email (SMTP)")
    smtp_server = st.text_input(
        "Servidor SMTP",
        value="smtp.gmail.com",
        help="Ex: smtp.gmail.com para Gmail"
    )
    smtp_port = st.number_input(
        "Porta SMTP",
        value=587,
        min_value=1,
        max_value=65535,
        help="Geralmente 587 para TLS"
    )
    email_user = st.text_input(
        "Email do remetente",
        help="Email que enviará os relatórios"
    )
    email_password = st.text_input(
        "Senha do email",
        type="password",
        help="Senha ou senha de app do email"
    )

    if st.button("💾 Salvar Configurações", use_container_width=True):
        try:
            db.salvar_config_rd_station('api_key', api_key)
            db.salvar_config_rd_station('email_destino', email_destino)
            db.salvar_config_rd_station('smtp_server', smtp_server)
            db.salvar_config_rd_station('smtp_port', str(smtp_port))
            db.salvar_config_rd_station('email_user', email_user)
            db.salvar_config_rd_station('email_password', email_password)
            st.success("✅ Configurações salvas com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {str(e)}")

# ===== ABAS PRINCIPAIS =====
tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "📋 Histórico", "⚡ Movimentações"])

# ===== TAB 1: DASHBOARD =====
with tab1:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Snapshot de Leads")
    with col2:
        if st.button("🔄 Atualizar", key="refresh_dashboard"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    # Buscar dados do banco
    snapshot_hoje = db.buscar_snapshot_hoje()
    snapshot_anterior = db.buscar_snapshot_anterior()

    if snapshot_hoje:
        # Calcular KPIs
        col1, col2, col3, col4 = st.columns(4)

        total_leads = sum(sum(stages.values()) for stages in snapshot_hoje.values())
        total_anterior = sum(sum(stages.values()) for stages in snapshot_anterior.values()) if snapshot_anterior else 0
        variacao = total_leads - total_anterior

        with col1:
            st.metric(
                "Total de Leads",
                total_leads,
                delta=variacao if variacao != 0 else None,
                delta_color="normal"
            )

        # Contar avanços
        movimentacoes = db.buscar_movimentacoes_hoje()
        if not movimentacoes.empty:
            avancos = len(movimentacoes[movimentacoes['movement_type'] == 'advancement'])
            retrocessos = len(movimentacoes[movimentacoes['movement_type'] == 'regression'])
            saidas = len(movimentacoes[movimentacoes['movement_type'] == 'exit'])

            with col2:
                st.metric("📈 Avanços", avancos)
            with col3:
                st.metric("📉 Retrocessos", retrocessos)
            with col4:
                st.metric("❌ Saídas", saidas)

        # Gráficos
        st.divider()

        # Preparar dados para gráficos
        funnels = list(snapshot_hoje.keys())
        colors_palette = px.colors.qualitative.Set2

        # Gráfico 1: Distribuição por Funil
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuição por Funil")
            funnel_data = []
            for funnel_name in funnels:
                total = sum(snapshot_hoje[funnel_name].values())
                funnel_data.append({"Funil": funnel_name, "Total": total})

            df_funnels = pd.DataFrame(funnel_data)
            if not df_funnels.empty:
                fig = px.pie(
                    df_funnels,
                    values="Total",
                    names="Funil",
                    color_discrete_sequence=colors_palette
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

        # Gráfico 2: Leads por Estágio (stacked bar)
        with col2:
            st.subheader("Leads por Estágio")

            stages_data = []
            for funnel_name in funnels:
                for stage_name, count in snapshot_hoje[funnel_name].items():
                    stages_data.append({
                        "Funil": funnel_name,
                        "Estágio": stage_name,
                        "Quantidade": count
                    })

            df_stages = pd.DataFrame(stages_data)
            if not df_stages.empty:
                fig = px.bar(
                    df_stages,
                    x="Funil",
                    y="Quantidade",
                    color="Estágio",
                    barmode="stack",
                    color_discrete_sequence=colors_palette
                )
                st.plotly_chart(fig, use_container_width=True)

        # Tabela detalhada por funil
        st.divider()
        st.subheader("📊 Detalhes por Funil")

        for funnel_name in sorted(funnels):
            with st.expander(f"🎯 {funnel_name}", expanded=True):
                stages_df = pd.DataFrame([
                    {"Estágio": stage, "Quantidade": count}
                    for stage, count in snapshot_hoje[funnel_name].items()
                ])
                st.dataframe(
                    stages_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Quantidade": st.column_config.NumberColumn(format="%d")
                    }
                )

    else:
        st.info("📭 Nenhum dado disponível ainda. Configure a API do RD Station e clique em 'Atualizar'.")

# ===== TAB 2: HISTÓRICO =====
with tab2:
    st.subheader("📋 Histórico de Snapshots")

    conn = db.conectar()
    df_historico = pd.read_sql(
        "SELECT DISTINCT data, COUNT(*) as registros FROM rd_station_leads GROUP BY data ORDER BY data DESC LIMIT 30",
        conn
    )
    conn.close()

    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True, hide_index=True)

        # Filtro de data
        datas_disponiveis = sorted(df_historico['data'].unique(), reverse=True)
        data_selecionada = st.selectbox(
            "Selecionar data para análise",
            datas_disponiveis,
            format_func=lambda x: f"📅 {x}"
        )

        if data_selecionada:
            conn = db.conectar()
            df_snapshot = pd.read_sql(
                "SELECT funnel_name, stage_name, lead_count FROM rd_station_leads WHERE data = ?",
                conn,
                params=(data_selecionada,)
            )
            conn.close()

            st.dataframe(df_snapshot, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Nenhum histórico disponível.")

# ===== TAB 3: MOVIMENTAÇÕES =====
with tab3:
    st.subheader("⚡ Histórico de Movimentações")

    conn = db.conectar()
    df_movimentos = pd.read_sql(
        "SELECT data, hora, funnel_name, stage_name, movement_type, quantity, description FROM rd_station_movimentacoes ORDER BY data DESC, hora DESC LIMIT 100",
        conn
    )
    conn.close()

    if not df_movimentos.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            tipo_filtro = st.selectbox(
                "Tipo de movimentação",
                ["Todas"] + sorted(df_movimentos['movement_type'].unique().tolist())
            )

        with col2:
            funil_filtro = st.selectbox(
                "Funil",
                ["Todos"] + sorted(df_movimentos['funnel_name'].unique().tolist())
            )

        with col3:
            data_inicio = st.date_input("Data inicial", value=datetime.now() - timedelta(days=30))

        # Aplicar filtros
        df_filtrado = df_movimentos.copy()

        if tipo_filtro != "Todas":
            df_filtrado = df_filtrado[df_filtrado['movement_type'] == tipo_filtro]

        if funil_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['funnel_name'] == funil_filtro]

        df_filtrado['data'] = pd.to_datetime(df_filtrado['data'])
        df_filtrado = df_filtrado[df_filtrado['data'].dt.date >= data_inicio]

        # Exibir tabela
        st.dataframe(
            df_filtrado[['data', 'hora', 'funnel_name', 'stage_name', 'movement_type', 'quantity', 'description']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "data": "Data",
                "hora": "Hora",
                "funnel_name": "Funil",
                "stage_name": "Estágio",
                "movement_type": "Tipo",
                "quantity": "Qtd",
                "description": "Descrição"
            }
        )

        # Estatísticas
        st.divider()
        st.subheader("📊 Estatísticas")

        col1, col2, col3 = st.columns(3)

        with col1:
            avancos = len(df_filtrado[df_filtrado['movement_type'] == 'advancement'])
            st.metric("📈 Total de Avanços", avancos)

        with col2:
            retrocessos = len(df_filtrado[df_filtrado['movement_type'] == 'regression'])
            st.metric("📉 Total de Retrocessos", retrocessos)

        with col3:
            saidas = len(df_filtrado[df_filtrado['movement_type'] == 'exit'])
            st.metric("❌ Total de Saídas", saidas)

    else:
        st.info("📭 Nenhuma movimentação registrada.")

# ===== RODAPÉ =====
st.divider()
st.caption(f"⏱️ Última atualização: {st.session_state.last_refresh.strftime('%d/%m/%Y %H:%M:%S')}")
st.caption("Sistema de Automação - RD Station | Dashboard de Leads e Funis")
