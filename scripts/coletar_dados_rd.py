#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Coleta dados do RD Station CRM e salva no Supabase.
Estrategia rapida: snapshot por estagio + ganhos/perdidos so de HOJE.

Uso:
    python scripts/coletar_dados_rd.py
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from scripts.rd_station_api import get_rd_station_client, FUNIS_COMERCIAL
from scripts.supabase_rd import salvar_snapshot, salvar_vendedores


def coletar():
    print("=" * 60)
    print("Coleta RD Station -> Supabase")
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 60)

    api_key = os.getenv("RD_STATION_API_KEY")
    if not api_key:
        raise ValueError("RD_STATION_API_KEY nao configurada")

    hoje = date.today()
    hoje_str = str(hoje)
    client = get_rd_station_client(api_key)

    # --- 1. Snapshot por estagio (rapido, ~17 chamadas) ---
    print("\n[1] Snapshot por estagio...")
    snapshot = client.get_snapshot_por_funis(FUNIS_COMERCIAL)
    salvar_snapshot(hoje, snapshot)
    print(f"OK: {sum(len(v) for v in snapshot.values())} estagios")

    # --- 2. Ganhos e perdidos SO DE HOJE por vendedor ---
    print("\n[2] Ganhos e perdidos de hoje...")
    ganhos_map = {}
    valor_map = {}
    perdidos_map = {}

    for pipeline_name, pid in FUNIS_COMERCIAL.items():
        deals_won = client._paginar_deals({
            "deal_pipeline_id": pid,
            "win": "true",
            "closed_at_from": hoje_str,
            "closed_at_to": hoje_str,
        })
        for deal in deals_won:
            user = deal.get("user", {}) or {}
            nome = (user.get("name") or "").strip()
            amt = float(deal.get("amount_total") or 0)
            if nome:
                ganhos_map[nome] = ganhos_map.get(nome, 0) + 1
                valor_map[nome] = valor_map.get(nome, 0.0) + amt

        deals_lost = client._paginar_deals({
            "deal_pipeline_id": pid,
            "lost": "true",
            "closed_at_from": hoje_str,
            "closed_at_to": hoje_str,
        })
        for deal in deals_lost:
            user = deal.get("user", {}) or {}
            nome = (user.get("name") or "").strip()
            if nome:
                perdidos_map[nome] = perdidos_map.get(nome, 0) + 1

        total_won = len(deals_won)
        total_lost = len(deals_lost)
        if total_won or total_lost:
            print(f"   {pipeline_name}: {total_won} ganhos | {total_lost} perdidos hoje")

    # Em andamento = soma do snapshot por vendedor nao temos sem paginar
    # Usamos totais do snapshot como proxy
    total_em_andamento = sum(
        count
        for funil, estagios in snapshot.items()
        for estagio, count in estagios.items()
        if list(estagios.keys()).index(estagio) > 0  # pula 1o estagio
    )

    # Montar lista de vendedores com dados de hoje
    todos_nomes = set(ganhos_map) | set(perdidos_map)
    vendedores = []
    for nome in todos_nomes:
        g = ganhos_map.get(nome, 0)
        p = perdidos_map.get(nome, 0)
        vendedores.append({
            "vendedor": nome,
            "criadas": g + p,
            "em_andamento": 0,
            "ganhos_3m": g,
            "perdidos_3m": p,
            "valor_ganhos_3m": valor_map.get(nome, 0.0),
        })

    vendedores.sort(key=lambda x: x["ganhos_3m"], reverse=True)

    print(f"\n[3] Salvando {len(vendedores)} vendedor(es) no Supabase...")
    if vendedores:
        salvar_vendedores(hoje, vendedores)
    else:
        print("   Nenhum deal finalizado hoje")

    print("\n" + "=" * 60)
    print(f"Coleta concluida! {hoje_str}")
    print(f"   Snapshot: {sum(len(v) for v in snapshot.values())} estagios")
    print(f"   Ganhos hoje: {sum(ganhos_map.values())} | Perdidos: {sum(perdidos_map.values())}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        coletar()
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\nERRO: {e}")
        traceback.print_exc()
        sys.exit(1)
