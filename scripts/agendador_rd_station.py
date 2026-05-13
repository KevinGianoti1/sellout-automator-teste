#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agendador de automação RD Station usando APScheduler.

Este script inicia um background scheduler que executa a automação
de relatórios diariamente às 8h da manhã.

Uso:
    python scripts/agendador_rd_station.py

Para parar o agendador, pressione Ctrl+C.
"""

import sys
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agendador_rd_station.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automatizar_relatorios import executar_automacao_rd_station


def job_relatorio_diario():
    """Job que será executado diariamente às 8h."""
    logger.info("🤖 Iniciando execução do relatório de RD Station")
    try:
        sucesso = executar_automacao_rd_station()
        if sucesso:
            logger.info("✅ Relatório gerado e enviado com sucesso")
        else:
            logger.error("❌ Falha ao gerar relatório")
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")


def iniciar_agendador(hora: int = 8, minuto: int = 0):
    """
    Inicia o agendador de tarefas.

    Args:
        hora: Hora do dia para executar (0-23). Padrão: 8 (8h da manhã)
        minuto: Minuto da hora. Padrão: 0
    """
    import os
    os.makedirs('logs', exist_ok=True)

    scheduler = BackgroundScheduler()

    # Agendar job para executar diariamente no horário especificado
    trigger = CronTrigger(hour=hora, minute=minuto)
    scheduler.add_job(
        job_relatorio_diario,
        trigger=trigger,
        id='relatorio_rd_station_diario',
        name='Relatório RD Station Diário',
        replace_existing=True
    )

    print("=" * 60)
    print("🚀 AGENDADOR RD STATION INICIADO")
    print("=" * 60)
    print(f"⏱️  Hora de execução: {hora:02d}:{minuto:02d} (todos os dias)")
    print(f"📅 Próxima execução: {scheduler.get_job('relatorio_rd_station_diario').next_run_time}")
    print("\nPressione Ctrl+C para parar o agendador")
    print("=" * 60)

    logger.info(f"🚀 Agendador iniciado - Execução diária às {hora:02d}:{minuto:02d}")

    try:
        scheduler.start()
        # Manter o programa rodando
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⛔ Agendador parado pelo usuário")
        print("=" * 60)
        logger.info("⛔ Agendador parado")
        scheduler.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agendador de automação RD Station"
    )
    parser.add_argument(
        '--hora',
        type=int,
        default=8,
        help='Hora do dia para executar (0-23). Padrão: 8'
    )
    parser.add_argument(
        '--minuto',
        type=int,
        default=0,
        help='Minuto da hora. Padrão: 0'
    )
    parser.add_argument(
        '--now',
        action='store_true',
        help='Executar uma vez imediatamente (teste)'
    )

    args = parser.parse_args()

    if args.now:
        print("🧪 Executando teste imediato...")
        executar_automacao_rd_station()
    else:
        if not (0 <= args.hora <= 23):
            print("❌ Hora deve estar entre 0 e 23")
            sys.exit(1)
        if not (0 <= args.minuto <= 59):
            print("❌ Minuto deve estar entre 0 e 59")
            sys.exit(1)

        iniciar_agendador(hora=args.hora, minuto=args.minuto)
