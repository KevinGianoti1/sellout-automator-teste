#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de automação para RD Station.
Executa diariamente às 8h da manhã:
1. Busca dados de leads do RD Station
2. Calcula movimentações em relação ao dia anterior
3. Gera relatório Excel
4. Envia por email
5. Armazena dados no banco de dados

Uso direto:
    python scripts/automatizar_relatorios.py

Com agendador (background):
    python scripts/agendador_rd_station.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import db
from scripts.rd_station_api import get_rd_station_client
from scripts.relatorio_rd_station import gerar_relatorio_excel, gerar_email_html
from scripts.email_automator import get_email_client_by_provider


def executar_automacao_rd_station():
    """Executa a automação completa de relatório de RD Station."""

    print("=" * 60)
    print("Iniciando automacao de RD Station")
    print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    try:
        # ===== ETAPA 0: Garantir tabelas =====
        db.criar_tabelas_rd_station()

        # ===== ETAPA 1: Obter configurações =====
        print("\n[1] Carregando configuracoes...")

        api_key = os.getenv('RD_STATION_API_KEY') or db.buscar_config_rd_station('api_key')
        email_destino = os.getenv('EMAIL_DESTINO') or db.buscar_config_rd_station('email_destino')
        smtp_server = os.getenv('SMTP_SERVER') or db.buscar_config_rd_station('smtp_server')
        smtp_port = int(os.getenv('SMTP_PORT', 587) or db.buscar_config_rd_station('smtp_port') or 587)
        email_user = os.getenv('EMAIL_USER') or db.buscar_config_rd_station('email_user')
        email_password = os.getenv('EMAIL_PASSWORD') or db.buscar_config_rd_station('email_password')

        if not all([api_key, email_destino, email_user, email_password]):
            raise ValueError(
                "ERRO: Configurações incompletas. Configure:\n"
                "   - RD_STATION_API_KEY\n"
                "   - EMAIL_DESTINO\n"
                "   - EMAIL_USER\n"
                "   - EMAIL_PASSWORD\n"
                "   - SMTP_SERVER (opcional, padrão: smtp.gmail.com)\n"
                "   - SMTP_PORT (opcional, padrão: 587)"
            )

        print("OK: Configurações carregadas")

        # ===== ETAPA 2: Criar tabelas =====
        print("\n[2]  Preparando banco de dados...")
        db.criar_tabelas_rd_station()
        print("OK: Banco de dados pronto")

        # ===== ETAPA 3: Buscar dados do RD Station =====
        print("\n[3]  Conectando ao RD Station...")
        client = get_rd_station_client(api_key)

        print("   Buscando funis e leads...")
        snapshot_atual = client.get_all_deals_by_stage()
        print(f"OK: {len(snapshot_atual)} funnel(s) encontrado(s)")

        # ===== ETAPA 4: Calcular movimentações =====
        print("\n[4]  Calculando movimentações...")
        snapshot_anterior = db.buscar_snapshot_anterior()

        if snapshot_anterior:
            movimentacoes = client.calculate_movements(snapshot_atual, snapshot_anterior)
            print(f"OK: Movimentações detectadas")
        else:
            movimentacoes = {}
            print("INFO:  Primeiro snapshot - sem movimentações anteriores")

        # ===== ETAPA 5: Salvar dados no banco =====
        print("\n[5]  Salvando dados no banco de dados...")
        db.salvar_snapshot_leads(snapshot_atual)
        if movimentacoes:
            db.salvar_movimentacoes(movimentacoes)
        print("OK: Dados salvos")

        # ===== ETAPA 6: Gerar relatório Excel =====
        print("\n[6]  Gerando relatório Excel...")
        os.makedirs("data/output", exist_ok=True)
        data_str = datetime.now().strftime("%Y-%m-%d")
        arquivo_excel = f"data/output/relatorio_leads_{data_str}.xlsx"

        gerar_relatorio_excel(snapshot_atual, movimentacoes, arquivo_excel)
        print(f"OK: Excel gerado: {arquivo_excel}")

        # ===== ETAPA 7: Gerar HTML para email =====
        print("\n[7]  Gerando email em HTML...")
        html_email = gerar_email_html(snapshot_atual, movimentacoes)
        print("OK: Email HTML gerado")

        # ===== ETAPA 8: Enviar email =====
        print("\n[8]  Enviando email...")
        try:
            email_client = get_email_client_by_provider(
                provider='gmail',  # Ajuste conforme necessário
                email_user=email_user,
                email_password=email_password
            )

            # Sobrescrever servidor se necessário
            email_client.smtp_server = smtp_server
            email_client.smtp_port = smtp_port

            sucesso = email_client.enviar_relatorio_rd_station(
                destinatarios=[email_destino],
                corpo_html=html_email,
                arquivo_excel=arquivo_excel
            )

            if sucesso:
                print(f"OK: Email enviado para {email_destino}")
            else:
                print(f"ERRO: Falha ao enviar email")

        except Exception as e:
            print(f"ERRO: Erro ao enviar email: {str(e)}")

        # ===== CONCLUSÃO =====
        print("\n" + "=" * 60)
        print("OK: Automação concluída com sucesso!")
        print("=" * 60)
        print(f"\n Resumo:")
        print(f"   - Total de leads: {sum(sum(s.values()) for s in snapshot_atual.values())}")
        print(f"   - Funis monitorados: {len(snapshot_atual)}")
        if movimentacoes:
            total_mov = sum(len(stages) for stages in movimentacoes.values())
            print(f"   - Movimentações detectadas: {total_mov}")
        print(f"   - Relatório salvo em: {arquivo_excel}")
        print(f"   - Email enviado para: {email_destino}")

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"ERRO: ERRO NA AUTOMAÇÃO: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    sucesso = executar_automacao_rd_station()
    sys.exit(0 if sucesso else 1)
