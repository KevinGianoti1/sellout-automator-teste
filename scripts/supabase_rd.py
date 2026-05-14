#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cliente Supabase via REST API (sem dependência extra além de requests)."""

import os
import requests
from datetime import date, timedelta
from typing import List, Dict, Optional

SUPABASE_URL = "https://wwtemgrjqgdtmertoktv.supabase.co"


def _headers() -> dict:
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not key:
        raise ValueError("SUPABASE_SERVICE_KEY nao configurada")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }


def _url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


def criar_tabelas():
    """Cria as tabelas via SQL direto (endpoint /rest/v1/rpc/exec_sql)."""
    sql = """
    CREATE TABLE IF NOT EXISTS rd_snapshot_estagios (
      id BIGSERIAL PRIMARY KEY,
      data DATE NOT NULL,
      funil TEXT NOT NULL,
      estagio TEXT NOT NULL,
      quantidade INTEGER NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS rd_vendedores_diario (
      id BIGSERIAL PRIMARY KEY,
      data DATE NOT NULL,
      vendedor TEXT NOT NULL,
      criadas INTEGER DEFAULT 0,
      em_andamento INTEGER DEFAULT 0,
      ganhos_3m INTEGER DEFAULT 0,
      perdidos_3m INTEGER DEFAULT 0,
      valor_ganhos_3m FLOAT DEFAULT 0,
      created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE UNIQUE INDEX IF NOT EXISTS uq_snapshot ON rd_snapshot_estagios(data, funil, estagio);
    CREATE UNIQUE INDEX IF NOT EXISTS uq_vendedor ON rd_vendedores_diario(data, vendedor);
    """
    h = _headers()
    h["Content-Type"] = "application/json"
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        json={"sql": sql},
        headers=h,
        timeout=30,
    )
    if resp.status_code not in (200, 204):
        print(f"   Aviso criar_tabelas: {resp.status_code} {resp.text[:200]}")


def _upsert(table: str, rows: list, on_conflict: str):
    h = _headers()
    h["Prefer"] = "resolution=merge-duplicates,return=minimal"
    resp = requests.post(
        f"{_url(table)}?on_conflict={on_conflict}",
        json=rows,
        headers=h,
        timeout=30,
    )
    resp.raise_for_status()


def salvar_snapshot(data_ref: date, snapshot: Dict[str, Dict[str, int]]):
    rows = [
        {"data": str(data_ref), "funil": funil, "estagio": estagio, "quantidade": qtd}
        for funil, estagios in snapshot.items()
        for estagio, qtd in estagios.items()
    ]
    if not rows:
        return
    _upsert("rd_snapshot_estagios", rows, "data,funil,estagio")
    print(f"   Snapshot salvo: {len(rows)} registros")


def salvar_vendedores(data_ref: date, vendedores: List[Dict]):
    rows = [
        {
            "data": str(data_ref),
            "vendedor": v["vendedor"],
            "criadas": v.get("criadas", 0),
            "em_andamento": v.get("em_andamento", 0),
            "ganhos_3m": v.get("ganhos_3m", 0),
            "perdidos_3m": v.get("perdidos_3m", 0),
            "valor_ganhos_3m": float(v.get("valor_ganhos_3m", 0)),
        }
        for v in vendedores
    ]
    if not rows:
        return
    _upsert("rd_vendedores_diario", rows, "data,vendedor")
    print(f"   Vendedores salvos: {len(rows)} registros")


def ler_vendedores(data_ref: Optional[date] = None) -> List[Dict]:
    if data_ref is None:
        data_ref = date.today()

    h = _headers()
    h.pop("Prefer", None)

    resp = requests.get(
        _url("rd_vendedores_diario"),
        params={"data": f"eq.{data_ref}", "order": "criadas.desc"},
        headers=h,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data:
        return data

    # fallback: ontem
    ontem = data_ref - timedelta(days=1)
    resp2 = requests.get(
        _url("rd_vendedores_diario"),
        params={"data": f"eq.{ontem}", "order": "criadas.desc"},
        headers=h,
        timeout=15,
    )
    resp2.raise_for_status()
    rows = resp2.json()
    if rows:
        print(f"   Usando dados de {ontem} (fallback)")
    return rows


def ler_snapshot(data_ref: Optional[date] = None) -> Dict[str, Dict[str, int]]:
    if data_ref is None:
        data_ref = date.today()

    h = _headers()
    h.pop("Prefer", None)

    resp = requests.get(
        _url("rd_snapshot_estagios"),
        params={"data": f"eq.{data_ref}"},
        headers=h,
        timeout=15,
    )
    resp.raise_for_status()
    rows = resp.json()

    if not rows:
        ontem = data_ref - timedelta(days=1)
        resp2 = requests.get(
            _url("rd_snapshot_estagios"),
            params={"data": f"eq.{ontem}"},
            headers=h,
            timeout=15,
        )
        resp2.raise_for_status()
        rows = resp2.json()

    result: Dict[str, Dict[str, int]] = {}
    for row in rows:
        result.setdefault(row["funil"], {})[row["estagio"]] = row["quantidade"]
    return result
