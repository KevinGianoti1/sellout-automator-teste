#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Envia email diário com dados do RD Station lidos do Supabase.
Roda às 8h BRT via GitHub Actions — executa em segundos.

Uso:
    python scripts/automatizar_relatorios.py
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from scripts.supabase_rd import ler_vendedores, ler_snapshot
from scripts.relatorio_rd_station import gerar_email_html_resumo
from scripts.email_automator import get_email_client_by_provider


def enviar_relatorio():
    print("=" * 60)
    print("Relatorio Comercial RD Station")
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 60)

    email_destino  = os.getenv("EMAIL_DESTINO")
    smtp_server    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port      = int(os.getenv("SMTP_PORT", 587))
    email_user     = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not all([email_destino, email_user, email_password]):
        raise ValueError("Variaveis de email incompletas")

    print("\n[1] Lendo dados do Supabase...")
    hoje = date.today()
    vendedores = ler_vendedores(hoje)
    snapshot = ler_snapshot(hoje)
    print(f"OK: {len(vendedores)} vendedores | {sum(len(v) for v in snapshot.values())} estagios")

    if not vendedores:
        print("AVISO: Sem dados de vendedores — email nao enviado")
        return False

    # Montar finalizados a partir do snapshot para o email
    finalizados = {}

    print("\n[2] Gerando email...")
    html = gerar_email_html_resumo(vendedores, finalizados, [], {})

    print("\n[3] Enviando email...")
    ec = get_email_client_by_provider("gmail", email_user, email_password)
    ec.smtp_server = smtp_server
    ec.smtp_port = smtp_port

    data_display = datetime.now().strftime("%d/%m/%Y")
    sucesso = ec.enviar_relatorio_rd_station(
        destinatarios=[email_destino],
        corpo_html=html,
        arquivo_excel=None,
        assunto=f"Relatorio Comercial RD Station - {data_display}",
    )

    if sucesso:
        print(f"OK: Email enviado para {email_destino}")
    else:
        print("ERRO: Falha ao enviar email")

    return sucesso


if __name__ == "__main__":
    try:
        ok = enviar_relatorio()
        sys.exit(0 if ok else 1)
    except Exception as e:
        import traceback
        print(f"\nERRO: {e}")
        traceback.print_exc()
        sys.exit(1)
