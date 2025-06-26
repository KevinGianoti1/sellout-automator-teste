
import pandas as pd
import streamlit as st

def estatisticas_gerais(df):
    st.subheader("📋 Estatísticas Gerais")
    st.write(f"Número de linhas: {df.shape[0]}")
    st.write(f"Número de colunas: {df.shape[1]}")
    st.write("Valores ausentes por coluna:")
    st.write(df.isnull().sum())
    st.write("Resumo estatístico:")
    st.write(df.describe())

def top_bottom_valores(df, col, n=5):
    st.subheader(f"🔝 Top {n} e 🔻 Bottom {n} de {col}")
    st.write(f"Top {n} maiores valores: {df[col].nlargest(n).values}")
    st.write(f"Top {n} menores valores: {df[col].nsmallest(n).values}")

def alerta_outlier(df, col):
    media = df[col].mean()
    std = df[col].std()
    maxv = df[col].max()
    minv = df[col].min()
    if maxv > media + 3 * std:
        st.warning(f"Possível outlier: valor máximo de {col} ({maxv:.2f}) muito acima da média ({media:.2f})")
    if minv < media - 3 * std:
