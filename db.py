import sqlite3
import pandas as pd
from datetime import datetime
import os

# 🔌 Conecta ao banco SQLite com verificação de pasta
def conectar():
    os.makedirs("data", exist_ok=True)  # Garante que a pasta 'data' existe
    return sqlite3.connect("data/historico.db")

# 💾 Salva Sell Out e Resumo no banco
def salvar_sellout(usuario, df_sellout, df_resumo):
    conn = conectar()
    data_upload = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df_sellout = df_sellout.copy()
    df_resumo = df_resumo.copy()

    df_sellout["Usuario"] = usuario
    df_resumo["Usuario"] = usuario
    df_sellout["Data Upload"] = data_upload
    df_resumo["Data Upload"] = data_upload

    df_sellout.to_sql("sellout", conn, if_exists="append", index=False)
    df_resumo.to_sql("resumo", conn, if_exists="append", index=False)

    conn.close()

# 💾 Salva apenas o Resumo
def salvar_resumo(usuario, df):
    conn = conectar()
    df = df.copy()
    df["Usuario"] = usuario
    df["Data Upload"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_sql("resumo", conn, if_exists="append", index=False)
    conn.close()

# 🔍 Busca histórico de Sell Out do usuário
def buscar_sellout(usuario):
    conn = conectar()
    try:
        df = pd.read_sql(
            "SELECT * FROM sellout WHERE Usuario = ?",
            conn,
            params=(usuario,)
        )
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# 🔍 Busca histórico de Resumo do usuário
def buscar_resumo(usuario):
    conn = conectar()

    # Cria a tabela se ainda não existir
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumo (
            Ano INTEGER,
            Código TEXT,
            Descrição TEXT,
            Qtde_Total INTEGER,
            Valor_Total TEXT,
            Preço_Mínimo TEXT,
            Preço_Máximo TEXT,
            Usuario TEXT,
            "Data Upload" TEXT
        )
    """)

    try:
        df = pd.read_sql(
            "SELECT * FROM resumo WHERE Usuario = ?",
            conn,
            params=(usuario,)
        )
    except Exception:
        df = pd.DataFrame()

    conn.close()
    return df

# RD Station - Gerenciamento de dados de leads e funis

def criar_tabelas_rd_station():
    """Cria as tabelas necessárias para armazenar dados do RD Station."""
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de snapshots de leads por funil/estágio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rd_station_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            hora TIME,
            funnel_name TEXT,
            stage_name TEXT,
            lead_count INTEGER,
            UNIQUE(data, funnel_name, stage_name)
        )
    """)

    # Tabela de movimentações de leads
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rd_station_movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            hora TIME,
            funnel_name TEXT,
            stage_name TEXT,
            movement_type TEXT,
            quantity INTEGER,
            description TEXT
        )
    """)

    # Tabela de configurações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rd_station_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE,
            config_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def salvar_snapshot_leads(snapshot_data: dict) -> None:
    """
    Salva snapshot de leads por funil e estágio.

    Args:
        snapshot_data: Dict com estrutura {funnel: {stage: count}}
    """
    conn = conectar()
    cursor = conn.cursor()

    hoje = datetime.now().strftime("%Y-%m-%d")
    agora = datetime.now().strftime("%H:%M:%S")

    for funnel_name, stages in snapshot_data.items():
        for stage_name, count in stages.items():
            cursor.execute("""
                INSERT OR REPLACE INTO rd_station_leads
                (data, hora, funnel_name, stage_name, lead_count)
                VALUES (?, ?, ?, ?, ?)
            """, (hoje, agora, funnel_name, stage_name, count))

    conn.commit()
    conn.close()

def salvar_movimentacoes(movements_data: dict) -> None:
    """
    Salva movimentações de leads detectadas.

    Args:
        movements_data: Dict com movimentações por funil e estágio
    """
    conn = conectar()
    cursor = conn.cursor()

    hoje = datetime.now().strftime("%Y-%m-%d")
    agora = datetime.now().strftime("%H:%M:%S")

    for funnel_name, stages in movements_data.items():
        for stage_name, movement in stages.items():
            movement_type = movement.get('type', 'unknown')
            quantity = movement.get('change', movement.get('count', 0))
            description = f"{quantity} lead(s) {movement_type} no estágio {stage_name}"

            cursor.execute("""
                INSERT INTO rd_station_movimentacoes
                (data, hora, funnel_name, stage_name, movement_type, quantity, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (hoje, agora, funnel_name, stage_name, movement_type, quantity, description))

    conn.commit()
    conn.close()

def buscar_snapshot_hoje() -> dict:
    """
    Busca snapshot de leads de hoje.

    Returns:
        Dict com estrutura {funnel: {stage: count}}
    """
    conn = conectar()
    df = pd.read_sql(
        "SELECT funnel_name, stage_name, lead_count FROM rd_station_leads WHERE data = DATE('now')",
        conn
    )
    conn.close()

    snapshot = {}
    for _, row in df.iterrows():
        funnel = row['funnel_name']
        stage = row['stage_name']
        count = row['lead_count']

        if funnel not in snapshot:
            snapshot[funnel] = {}
        snapshot[funnel][stage] = count

    return snapshot

def buscar_snapshot_anterior() -> dict:
    """
    Busca o snapshot anterior (último dia com dados).

    Returns:
        Dict com estrutura {funnel: {stage: count}}
    """
    conn = conectar()
    df = pd.read_sql("""
        SELECT funnel_name, stage_name, lead_count FROM rd_station_leads
        WHERE data = (SELECT MAX(data) FROM rd_station_leads WHERE data < DATE('now'))
    """, conn)
    conn.close()

    snapshot = {}
    for _, row in df.iterrows():
        funnel = row['funnel_name']
        stage = row['stage_name']
        count = row['lead_count']

        if funnel not in snapshot:
            snapshot[funnel] = {}
        snapshot[funnel][stage] = count

    return snapshot

def buscar_movimentacoes_hoje() -> pd.DataFrame:
    """
    Busca todas as movimentações registradas de hoje.

    Returns:
        DataFrame com movimentações
    """
    conn = conectar()
    df = pd.read_sql(
        "SELECT * FROM rd_station_movimentacoes WHERE data = DATE('now') ORDER BY hora DESC",
        conn
    )
    conn.close()
    return df

def salvar_config_rd_station(chave: str, valor: str) -> None:
    """
    Salva configuração do RD Station.

    Args:
        chave: Chave da configuração
        valor: Valor da configuração
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rd_station_config (config_key, config_value)
        VALUES (?, ?)
    """, (chave, valor))
    conn.commit()
    conn.close()

def buscar_config_rd_station(chave: str) -> str:
    """
    Busca valor de configuração do RD Station.

    Args:
        chave: Chave da configuração

    Returns:
        Valor da configuração ou None
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT config_value FROM rd_station_config WHERE config_key = ?",
        (chave,)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None
