import pandas as pd
import plotly.express as px

# 📊 Gera a Tabela Sell Out por Cliente, Ano e Mês
def gerar_sellout(df):
    df["Ano"] = df["Emissão"].dt.year
    df["Mês"] = df["Emissão"].dt.month

    meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    df["Mês Nome"] = df["Mês"].map(lambda x: meses_ordem[x - 1])
    df["Mês Nome"] = pd.Categorical(df["Mês Nome"], categories=meses_ordem, ordered=True)

    pivot = df.pivot_table(
        index=["Cliente", "Ano"],
        columns="Mês Nome",
        values="Total",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for mes in meses_ordem:
        if mes in pivot.columns:
            pivot[mes] = pd.to_numeric(pivot[mes], errors="coerce").fillna(0.0)

    return pivot

# 🧾 Gera Resumo de Itens Vendidos com Estatísticas por Ano
def gerar_resumo_itens(df):
    df.columns = df.columns.str.strip()
    df["Ano"] = df["Emissão"].dt.year

    if "Descrição" not in df.columns:
        raise ValueError("Coluna 'Descrição' não encontrada no DataFrame. Verifique o nome das colunas.")

    resumo = df.groupby(["Ano", "Código", "Descrição"]).agg(
        Qtde_Total=("Qtde", "sum"),
        Valor_Total=("Total", "sum"),
        Preço_Mínimo=("Valor Unit", "min"),
        Preço_Máximo=("Valor Unit", "max")
    ).reset_index()

    return resumo

# 📁 Exporta relatório completo para Excel
def salvar_relatorio_completo(sellout, resumo, caminho_arquivo):
    with pd.ExcelWriter(caminho_arquivo, engine="xlsxwriter") as writer:
        sellout.to_excel(writer, index=False, sheet_name="SellOut+Resumo", startrow=0)
        resumo.to_excel(writer, index=False, sheet_name="SellOut+Resumo", startrow=len(sellout) + 3)

# 📈 Gera gráfico de barras com somatório geral de vendas por mês
def plotar_grafico_sellout(df_sellout, ano=None):
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    df_filtrado = df_sellout.copy()
    if ano is not None:
        df_filtrado = df_filtrado[df_filtrado["Ano"] == ano]

    df_totais = df_filtrado[meses].sum().reset_index()
    df_totais.columns = ["Mês", "Total"]
    df_totais["Total"] = pd.to_numeric(df_totais["Total"], errors="coerce").fillna(0.0)
    df_totais["Mês"] = pd.Categorical(df_totais["Mês"], categories=meses, ordered=True)
    df_totais = df_totais.sort_values("Mês")

    df_totais["Texto"] = df_totais["Total"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    )

    y_max = df_totais["Total"].max()
    padding = y_max * 0.1 if y_max > 0 else 1000
    escala_final = y_max + padding

    fig = px.bar(
        df_totais,
        x="Mês",
        y="Total",
        text="Texto",
        title="📊 Total de Vendas por Mês (Somatório Geral)",
        labels={"Total": "Valor em R$"}
    )

    fig.update_layout(
        yaxis_title="Total (R$)",
        xaxis_title="Mês",
        plot_bgcolor="white",
        bargap=0.15,
        font=dict(color="black", size=14),
        yaxis=dict(
            tickprefix="R$ ",
            separatethousands=True,
            range=[0, escala_final]
        )
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="black", size=12),
        marker_color="#38bdf8"
    )

    return fig
