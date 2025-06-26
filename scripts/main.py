
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import openai
import os
from dotenv import load_dotenv

# Carrega variáveis do .env, inclusive OPENAI_API_KEY
load_dotenv()

# 📁 Caminhos
input_path = Path("data/input")
output_path = Path("data/output")
output_path.mkdir(exist_ok=True)

# 📥 Localiza o primeiro arquivo .xlsx
arquivo = next(input_path.glob("*.xlsx"), None)
if not arquivo:
    raise FileNotFoundError("Nenhum arquivo Excel encontrado em data/input")

print(f"🔍 Lendo arquivo: {arquivo.name}")
df = pd.read_excel(arquivo)

# 🧮 Calcula o total e extrai o ano da data de emissão
df["Total Calculado"] = df["Qtde"] * df["Valor Unit"]
df["Ano"] = pd.to_datetime(df["Emissão"]).dt.year

# 🧑‍🤝‍🧑 Separar por representante
col_representante = "Repre"
representantes = df[col_representante].dropna().unique()

def gerar_grafico(df_rep, nome_arquivo_grafico):
    # Exemplo: Vendas por mês
    df_rep['Mês'] = pd.to_datetime(df_rep['Emissão']).dt.month
    vendas_mes = df_rep.groupby('Mês')["Total Calculado"].sum()
    plt.figure(figsize=(8, 4))
    vendas_mes.plot(kind='bar')
    plt.title("Total de Vendas por Mês")
    plt.ylabel("R$ Vendido")
    plt.xlabel("Mês")
    plt.tight_layout()
    plt.savefig(nome_arquivo_grafico)
    plt.close()

def gerar_analise_gpt(df_rep):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return "Chave OpenAI não encontrada. Crie um arquivo .env com OPENAI_API_KEY=sua_chave"
    openai.api_key = openai_api_key
    resumo = df_rep.describe().to_string()
    prompt = (
        f"Analise os resultados de vendas abaixo e dê um resumo dos principais pontos, tendências e sugestões de melhoria:\n{resumo}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        analise = response['choices'][0]['message']['content']
    except Exception as e:
        analise = f"Erro ao gerar análise com o ChatGPT: {e}"
    return analise

for rep in representantes:
    df_rep = df[df[col_representante] == rep].copy()

    # Organiza colunas na ordem desejada
    colunas_finais = [
        "Ano", "Emissão", "Notas", "Cliente", "Código", "Descrição",
        "Qtde", "Valor Unit", "Total Calculado", "UF", "Empresa"
    ]
    df_saida = df_rep[colunas_finais].sort_values(by=["Ano", "Emissão"])

    # Salva o arquivo Excel básico
    nome_arquivo = f"Sell Out 2.0 - {rep}.xlsx"
    caminho_saida = output_path / nome_arquivo
    df_saida.to_excel(caminho_saida, index=False)

    # Gera gráfico e insere no Excel
    nome_arquivo_grafico = output_path / f"grafico_{rep}.png"
    gerar_grafico(df_rep, nome_arquivo_grafico)
    wb = load_workbook(caminho_saida)
    ws = wb.active
    img = Image(str(nome_arquivo_grafico))
    ws.add_image(img, 'L2')  # posição do gráfico
    wb.save(caminho_saida)
    os.remove(nome_arquivo_grafico)

    # Gera análise com ChatGPT e insere em uma aba nova
    analise_gpt = gerar_analise_gpt(df_rep)
    ws_analise = wb.create_sheet("Análise GPT")
    ws_analise["A1"] = "Análise automática do ChatGPT:"
    for i, linha in enumerate(analise_gpt.split('\n'), 2):
        ws_analise[f"A{i}"] = linha
    wb.save(caminho_saida)

    print(f"✅ Gerado: {nome_arquivo} com gráfico e análise GPT")

print("\n🎉 Relatórios por representante gerados com sucesso!")
