import os
import sys
import logging
import argparse
import smtplib
import requests
import pathlib
from datetime import datetime, timezone, timedelta
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

# Carrega .env do diretório atual
env_path = pathlib.Path(".env").resolve()
load_dotenv(dotenv_path=str(env_path), override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------

def fetch_relatorio(data_filtro: str | None = None) -> list[dict]:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_KEY", "")

    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não configurados no .env")

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    if data_filtro:
        date_filter = data_filtro
        log.info("Filtrando por data informada: %s", date_filter)
    else:
        # Usa a data atual de Brasília (UTC-3) para evitar usar dados de ontem
        # quando o servidor está em UTC e o dia já virou lá mas não aqui.
        brasilia = timezone(timedelta(hours=-3))
        date_filter = datetime.now(brasilia).strftime("%Y-%m-%d")
        log.info("Data atual em Brasília (UTC-3): %s", date_filter)

    resp = requests.get(
        f"{url}/rest/v1/relatorio_comercial_diario",
        headers=headers,
        params={
            "select": "*",
            "data": f"eq.{date_filter}",
            "order": "equipe.asc,vendedor.asc",
        },
        timeout=30,
    )
    resp.raise_for_status()
    rows = resp.json()
    log.info("Registros carregados: %d", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------

def fmt_brl(value) -> str:
    if value is None:
        return "R$ 0,00"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "R$ 0,00"
    return f"R$ {v:_.2f}".replace("_", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value) -> str:
    if value is None:
        return "0,00%"
    try:
        return f"{float(value):.2f}%".replace(".", ",")
    except (TypeError, ValueError):
        return "0,00%"


# ---------------------------------------------------------------------------
# Resumo executivo
# ---------------------------------------------------------------------------

def build_summary(rows: list[dict]) -> dict:
    total_vendedores = len(rows)
    atingiram = sum(1 for r in rows if r.get("status_meta") == "ATINGIU")
    pct_atingiu = (atingiram / total_vendedores * 100) if total_vendedores else 0
    projecao_total = sum(float(r.get("projecao") or 0) for r in rows)
    meta_mensal_total = sum(float(r.get("meta_mensal") or 0) for r in rows)
    pct_global = (projecao_total / meta_mensal_total * 100) if meta_mensal_total else 0
    data_ref = rows[0].get("data", "") if rows else ""
    mes_vendas = rows[0].get("mes_vendas", "") if rows else ""
    return {
        "total_vendedores": total_vendedores,
        "atingiram": atingiram,
        "pct_atingiu": pct_atingiu,
        "projecao_total": projecao_total,
        "meta_mensal_total": meta_mensal_total,
        "pct_global": pct_global,
        "data_ref": data_ref,
        "mes_vendas": mes_vendas,
    }


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def _status_badge(status: str) -> str:
    cfg = {
        "ATINGIU": ("#dcfce7", "#166534", "✅", "META BATIDA"),
        "QUASE":   ("#fef9c3", "#854d0e", "⚠️", "QUASE"),
        "ABAIXO":  ("#fee2e2", "#991b1b", "❌", "ABAIXO"),
    }
    bg, color, icon, label = cfg.get(status, ("#f3f4f6", "#374151", "", status))
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
        f'border-radius:9999px;font-size:11px;font-weight:700;'
        f'background:{bg};color:{color};">{icon} {label}</span>'
    )


def _progress_bar(value) -> str:
    try:
        v = min(float(value or 0), 100)
    except (TypeError, ValueError):
        v = 0
    if v >= 100:
        bar_color = "#16a34a"
    elif v >= 80:
        bar_color = "#ca8a04"
    else:
        bar_color = "#dc2626"
    pct_txt = fmt_pct(value)
    return (
        f'<div style="min-width:100px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:11px;font-weight:600;color:{bar_color};margin-bottom:3px;">'
        f'<span>{pct_txt}</span></div>'
        f'<div style="background:#e5e7eb;border-radius:9999px;height:6px;overflow:hidden;">'
        f'<div style="width:{v:.1f}%;background:{bar_color};height:100%;border-radius:9999px;transition:width .4s;"></div>'
        f'</div></div>'
    )


def _pct_color(value) -> str:
    try:
        v = float(value or 0)
    except (TypeError, ValueError):
        v = 0
    if v >= 100:
        return "#16a34a"
    if v >= 80:
        return "#ca8a04"
    return "#dc2626"


def _falta_cell(value) -> str:
    try:
        v = float(value or 0)
    except (TypeError, ValueError):
        v = 0
    color = "#dc2626" if v > 0 else "#16a34a"
    return f'<span style="color:{color};font-weight:500;">{fmt_brl(v)}</span>'


# paleta de equipes: (row_bg, badge_bg, badge_color, border_left_color)
_EQUIPE_PALETTE = [
    ("#eff6ff", "#1d4ed8", "#ffffff", "#3b82f6"),
    ("#faf5ff", "#6d28d9", "#ffffff", "#8b5cf6"),
    ("#fff7ed", "#c2410c", "#ffffff", "#f97316"),
    ("#f0fdf4", "#15803d", "#ffffff", "#22c55e"),
    ("#fdf2f8", "#9d174d", "#ffffff", "#ec4899"),
]


def build_html(rows: list[dict], summary: dict) -> str:
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data_fmt = datetime.strptime(summary["data_ref"], "%Y-%m-%d").strftime("%d/%m/%Y") if summary["data_ref"] else ""

    equipes: dict[str, list] = {}
    for r in rows:
        equipes.setdefault(r.get("equipe", "—"), []).append(r)

    table_rows_html = []
    for idx, (equipe, membros) in enumerate(equipes.items()):
        row_bg, badge_bg, badge_color, border_color = _EQUIPE_PALETTE[idx % len(_EQUIPE_PALETTE)]
        for i, r in enumerate(membros):
            status = r.get("status_meta", "")
            is_atingiu = status == "ATINGIU"
            row_style = (
                f'background:{row_bg};border-left:3px solid #16a34a;'
                if is_atingiu
                else f'background:{row_bg};border-left:3px solid {border_color};'
            )
            equipe_cell = ""
            if i == 0:
                equipe_cell = (
                    f'<td rowspan="{len(membros)}" style="vertical-align:middle;text-align:center;'
                    f'padding:8px 10px;border-right:1px solid #e5e7eb;white-space:nowrap;">'
                    f'<span style="display:inline-block;padding:4px 10px;border-radius:6px;'
                    f'font-weight:800;font-size:11px;letter-spacing:.5px;'
                    f'background:{badge_bg};color:{badge_color};">{equipe}</span>'
                    f"</td>"
                )
            falta_mensal = float(r.get("falta_para_meta_mensal") or 0)
            vendedor_extra = (
                ' <span style="font-size:10px;background:#dcfce7;color:#166534;'
                'border-radius:4px;padding:1px 5px;font-weight:700;">⭐ META</span>'
                if is_atingiu else ""
            )
            table_rows_html.append(
                f'<tr style="{row_style}">'
                + equipe_cell
                + f'<td style="padding:10px 10px;font-weight:600;color:#1e293b;white-space:nowrap;">'
                  f'{r.get("vendedor","")}{vendedor_extra}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;">{fmt_brl(r.get("projecao"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Pedidos em processo de faturamento">{fmt_brl(r.get("processo_faturamento"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Pedidos para remessa futura">{fmt_brl(r.get("remessa_futura"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Orçamentos em aberto">{fmt_brl(r.get("orcamento_aberto"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;font-weight:700;white-space:nowrap;" title="Projeção + Proc. Fat. + Rem. Futura + Orc. Aberto">{fmt_brl(r.get("total_comprometido"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Meta do dia corrente">{fmt_brl(r.get("meta_diaria"))}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Meta para o mês completo">{fmt_brl(r.get("meta_mensal"))}</td>'
                + f'<td style="padding:8px 14px;min-width:130px;">{_progress_bar(r.get("perc_meta_mensal"))}</td>'
                + f'<td style="padding:8px 10px;text-align:center;white-space:nowrap;">{_status_badge(status)}</td>'
                + f'<td style="padding:8px 10px;text-align:right;white-space:nowrap;" title="Quanto ainda falta para a meta mensal">{_falta_cell(falta_mensal)}</td>'
                + "</tr>"
            )

    table_html = "\n".join(table_rows_html)
    pct_global = float(summary["pct_global"])
    pct_global_color = _pct_color(pct_global)

    # mini progress bar global para o card
    global_bar_pct = min(pct_global, 100)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Relatório Comercial Diário – {data_fmt}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', system-ui, sans-serif;
      background: #f1f5f9;
      color: #1e293b;
      min-height: 100vh;
    }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #e2e8f0; }}
    th {{ position: relative; }}
    th[title]:hover::after {{
      content: attr(title);
      position: absolute;
      bottom: 110%;
      left: 50%;
      transform: translateX(-50%);
      background: #1e293b;
      color: #fff;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      white-space: nowrap;
      pointer-events: none;
      z-index: 10;
    }}
    @media (max-width: 768px) {{
      .cards-grid {{ grid-template-columns: 1fr 1fr !important; }}
      .hide-mobile {{ display: none !important; }}
      .table-wrap {{ font-size: 12px; }}
    }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #0f172a; color: #e2e8f0; }}
      .card {{ background: #1e293b !important; border-color: #334155 !important; }}
      .card-label {{ color: #94a3b8 !important; }}
      .section-header {{ background: #1e293b !important; border-color: #334155 !important; }}
      .table-head {{ background: #1e293b !important; }}
      th, td {{ border-color: #334155 !important; }}
      .section-wrap {{ background: #1e293b !important; border-color: #334155 !important; }}
    }}
    @media print {{ .no-print {{ display: none; }} }}
  </style>
</head>
<body>

<!-- HEADER -->
<header style="background:linear-gradient(135deg,#1d4ed8 0%,#1e3a8a 60%,#0f172a 100%);
               color:#fff;box-shadow:0 4px 24px rgba(0,0,0,.25);">
  <div style="max-width:1400px;margin:0 auto;padding:24px 28px;
              display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
    <div style="display:flex;align-items:center;gap:16px;">
      <!-- Logo placeholder -->
      <div style="width:48px;height:48px;background:rgba(255,255,255,.15);border-radius:12px;
                  display:flex;align-items:center;justify-content:center;font-size:24px;">📊</div>
      <div>
        <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#93c5fd;font-weight:600;margin-bottom:2px;">
          Dashboard Comercial
        </div>
        <h1 style="font-size:22px;font-weight:800;letter-spacing:-.3px;">Relatório Comercial Diário</h1>
        <div style="font-size:13px;color:#bfdbfe;margin-top:2px;">
          Mês de referência: <strong style="color:#fff;">{summary['mes_vendas']}</strong>
        </div>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#93c5fd;text-transform:uppercase;letter-spacing:1px;">Data do Relatório</div>
      <div style="font-size:28px;font-weight:800;letter-spacing:-.5px;">{data_fmt}</div>
    </div>
  </div>
</header>

<main style="max-width:1400px;margin:0 auto;padding:28px 16px;">

  <!-- RESUMO EXECUTIVO -->
  <div style="margin-bottom:8px;">
    <h2 style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;
               color:#64748b;margin-bottom:16px;">Resumo Executivo</h2>
    <div class="cards-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;">

      <div class="card" style="background:#fff;border-radius:16px;padding:20px;
                                border:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(0,0,0,.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <span class="card-label" style="font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#64748b;">Total Vendedores</span>
          <span style="font-size:22px;">👥</span>
        </div>
        <div style="font-size:40px;font-weight:800;color:#1e293b;line-height:1.1;margin-top:8px;">
          {summary['total_vendedores']}
        </div>
        <div style="font-size:12px;color:#94a3b8;margin-top:4px;">vendedores ativos</div>
      </div>

      <div class="card" style="background:#fff;border-radius:16px;padding:20px;
                                border:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(0,0,0,.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <span class="card-label" style="font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#64748b;">Atingiram a Meta</span>
          <span style="font-size:22px;">🏆</span>
        </div>
        <div style="font-size:40px;font-weight:800;color:#16a34a;line-height:1.1;margin-top:8px;">
          {summary['atingiram']}
        </div>
        <div style="font-size:12px;color:#94a3b8;margin-top:4px;">{fmt_pct(summary['pct_atingiu'])} do time</div>
      </div>

      <div class="card" style="background:#fff;border-radius:16px;padding:20px;
                                border:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(0,0,0,.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <span class="card-label" style="font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#64748b;">Projeção Total</span>
          <span style="font-size:22px;">💰</span>
        </div>
        <div style="font-size:18px;font-weight:800;color:#1d4ed8;line-height:1.2;margin-top:8px;">
          {fmt_brl(summary['projecao_total'])}
        </div>
        <div style="font-size:12px;color:#94a3b8;margin-top:4px;">valor projetado</div>
      </div>

      <div class="card" style="background:#fff;border-radius:16px;padding:20px;
                                border:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(0,0,0,.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <span class="card-label" style="font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#64748b;">Meta Mensal Total</span>
          <span style="font-size:22px;">🎯</span>
        </div>
        <div style="font-size:18px;font-weight:800;color:#475569;line-height:1.2;margin-top:8px;">
          {fmt_brl(summary['meta_mensal_total'])}
        </div>
        <div style="font-size:12px;color:#94a3b8;margin-top:4px;">alvo do mês</div>
      </div>

      <div class="card" style="background:#fff;border-radius:16px;padding:20px;
                                border:1px solid #e2e8f0;box-shadow:0 2px 12px rgba(0,0,0,.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
          <span class="card-label" style="font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#64748b;">% Global Atingido</span>
          <span style="font-size:22px;">📈</span>
        </div>
        <div style="font-size:36px;font-weight:800;color:{pct_global_color};line-height:1.1;margin-top:8px;">
          {fmt_pct(summary['pct_global'])}
        </div>
        <div style="background:#e5e7eb;border-radius:9999px;height:6px;margin-top:10px;overflow:hidden;">
          <div style="width:{global_bar_pct:.1f}%;background:{pct_global_color};height:100%;border-radius:9999px;"></div>
        </div>
      </div>

    </div>
  </div>

  <!-- TABELA PRINCIPAL -->
  <div class="section-wrap" style="background:#fff;border-radius:16px;border:1px solid #e2e8f0;
       box-shadow:0 2px 12px rgba(0,0,0,.06);overflow:hidden;margin-top:28px;">
    <div class="section-header" style="padding:18px 24px;border-bottom:1px solid #e2e8f0;
         display:flex;align-items:center;justify-content:space-between;">
      <h2 style="font-size:15px;font-weight:700;color:#1e293b;">Detalhamento por Vendedor</h2>
      <span style="font-size:12px;color:#94a3b8;">{summary['total_vendedores']} registros</span>
    </div>
    <div class="table-wrap" style="overflow-x:auto;">
      <table>
        <thead class="table-head" style="background:#f8fafc;">
          <tr>
            <th style="padding:10px 10px;text-align:center;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;white-space:nowrap;">Equipe</th>
            <th style="padding:10px 10px;text-align:left;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;">Vendedor</th>
            <th title="Valor de pedidos com alta probabilidade de fechamento"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Projeção ❓</th>
            <th title="Pedidos que já entraram no processo de faturamento"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Proc. Fat. ❓</th>
            <th title="Pedidos confirmados para entrega futura"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Rem. Futura ❓</th>
            <th title="Orçamentos enviados ainda em aberto"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Orc. Aberto ❓</th>
            <th title="Soma de Projeção + Proc. Fat. + Rem. Futura + Orc. Aberto"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Total Comp. ❓</th>
            <th title="Meta proporcional ao dia corrente do mês"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Meta Diária ❓</th>
            <th title="Meta total para o mês vigente"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Meta Mensal ❓</th>
            <th title="Percentual da meta mensal já comprometido"
                style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">% Meta Mensal ❓</th>
            <th style="padding:10px 10px;text-align:center;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;white-space:nowrap;">Status</th>
            <th title="Quanto ainda falta para atingir a meta mensal"
                style="padding:10px 10px;text-align:right;font-size:11px;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px;color:#64748b;cursor:help;white-space:nowrap;">Falta Mensal ❓</th>
          </tr>
        </thead>
        <tbody>
          {table_html}
        </tbody>
      </table>
    </div>
  </div>

</main>

<!-- FOOTER -->
<footer style="text-align:center;padding:32px 16px;margin-top:8px;">
  <div style="display:inline-flex;align-items:center;gap:12px;font-size:12px;color:#94a3b8;">
    <span>📊 Relatório Comercial Diário</span>
    <span>•</span>
    <span>Gerado em {now_str}</span>
    <span>•</span>
    <span>MAXIFORCE</span>
  </div>
</footer>

</body>
</html>"""


# ---------------------------------------------------------------------------
# E-mail
# ---------------------------------------------------------------------------

def _build_email_body(summary: dict) -> str:
    """HTML leve para o corpo do e-mail — compatível com Gmail e Outlook."""
    data_fmt = (
        datetime.strptime(summary["data_ref"], "%Y-%m-%d").strftime("%d/%m/%Y")
        if summary["data_ref"] else ""
    )
    pct_color = "#16a34a" if summary["pct_global"] >= 100 else ("#ca8a04" if summary["pct_global"] >= 80 else "#dc2626")
    kpis = [
        ("👥", "Total de vendedores", str(summary["total_vendedores"])),
        ("🏆", "Atingiram a meta", f"{summary['atingiram']} ({fmt_pct(summary['pct_atingiu'])})"),
        ("💰", "Projeção total", fmt_brl(summary["projecao_total"])),
        ("🎯", "Meta mensal total", fmt_brl(summary["meta_mensal_total"])),
        ("📈", "% Global atingido", fmt_pct(summary["pct_global"])),
    ]
    kpi_rows = "".join(
        f"""<tr>
          <td style="padding:10px 16px;font-size:20px;width:40px;">{icon}</td>
          <td style="padding:10px 0;font-size:14px;color:#475569;">{label}</td>
          <td style="padding:10px 16px;font-size:14px;font-weight:700;color:#1e293b;text-align:right;">{value}</td>
        </tr>"""
        for icon, label, value in kpis
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Relatório Comercial</title></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
  <!-- pré-header oculto -->
  <span style="display:none;max-height:0;overflow:hidden;color:#f1f5f9;">
    Confira os resultados comerciais do dia {data_fmt}
  </span>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:16px;overflow:hidden;
                    box-shadow:0 4px 24px rgba(0,0,0,.08);max-width:100%;">

        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#1d4ed8,#0f172a);padding:28px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <div style="font-size:11px;color:#93c5fd;text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">
                    Dashboard Comercial
                  </div>
                  <div style="font-size:22px;font-weight:700;color:#fff;">
                    📊 Relatório Comercial Diário
                  </div>
                  <div style="font-size:13px;color:#bfdbfe;margin-top:4px;">
                    Mês de referência: <strong style="color:#fff;">{summary['mes_vendas']}</strong>
                  </div>
                </td>
                <td align="right" style="vertical-align:top;">
                  <div style="font-size:11px;color:#93c5fd;text-transform:uppercase;letter-spacing:1px;">Data</div>
                  <div style="font-size:26px;font-weight:800;color:#fff;">{data_fmt}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- KPIs -->
        <tr>
          <td style="padding:28px 32px;">
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;
                        color:#64748b;margin-bottom:12px;">Resumo do Dia</div>
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
              {kpi_rows}
            </table>
          </td>
        </tr>

        <!-- % GLOBAL BAR -->
        <tr>
          <td style="padding:0 32px 24px;">
            <div style="font-size:12px;color:#64748b;margin-bottom:6px;">
              Performance global: <strong style="color:{pct_color};">{fmt_pct(summary['pct_global'])}</strong>
            </div>
            <div style="background:#e5e7eb;border-radius:9999px;height:8px;overflow:hidden;">
              <div style="width:{min(summary['pct_global'], 100):.1f}%;background:{pct_color};height:100%;border-radius:9999px;"></div>
            </div>
          </td>
        </tr>

        <!-- AVISO ANEXO -->
        <tr>
          <td style="padding:0 32px 28px;">
            <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px 18px;
                        font-size:13px;color:#1e40af;">
              📎 O relatório completo com todos os detalhes por vendedor está anexado a este e-mail.
            </div>
          </td>
        </tr>

        <!-- RODAPÉ -->
        <tr>
          <td style="background:#f8fafc;padding:18px 32px;border-top:1px solid #e2e8f0;
                     text-align:center;font-size:11px;color:#94a3b8;">
            Gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} &nbsp;•&nbsp; MAXIFORCE
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(html: str, summary: dict, recipients_override: list[str] | None = None) -> None:
    user = os.environ.get("EMAIL_USER", "")
    password = os.environ.get("EMAIL_PASSWORD", "")
    if recipients_override is not None:
        recipients = recipients_override
    else:
        to_raw = os.environ.get("EMAIL_TO", "")
        recipients = [e.strip() for e in to_raw.split(",") if e.strip()]

    if not (user and password and recipients):
        log.error("Credenciais de e-mail incompletas — verifique EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO.")
        return

    data_fmt = (
        datetime.strptime(summary["data_ref"], "%Y-%m-%d").strftime("%d/%m/%Y")
        if summary["data_ref"] else summary["data_ref"]
    )
    projecao_fmt = fmt_brl(summary["projecao_total"])
    subject = f"📊 Relatório Comercial Diário - {data_fmt} | Projeção: {projecao_fmt}"

    # mensagem raiz: mixed (corpo alternativo + anexo)
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(recipients)

    # parte alternativa (texto simples + HTML resumido)
    alt = MIMEMultipart("alternative")
    plain = (
        f"Relatório Comercial Diário - {data_fmt}\n"
        f"Projeção total: {projecao_fmt}\n"
        f"Vendedores: {summary['total_vendedores']} | Atingiram meta: {summary['atingiram']}\n"
        f"% Global: {fmt_pct(summary['pct_global'])}\n\n"
        f"O relatório completo está em anexo."
    )
    alt.attach(MIMEText(plain, "plain", "utf-8"))
    alt.attach(MIMEText(_build_email_body(summary), "html", "utf-8"))
    msg.attach(alt)

    # anexo: HTML completo
    attachment = MIMEBase("text", "html")
    attachment.set_payload(html.encode("utf-8"))
    encoders.encode_base64(attachment)
    filename = f"relatorio_comercial_{summary['data_ref']}.html"
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(user, password)
            smtp.sendmail(user, recipients, msg.as_string())
        log.info("E-mail enviado para: %s", recipients)
    except Exception as exc:
        log.error("Falha ao enviar e-mail: %s", exc)


# ---------------------------------------------------------------------------
# WhatsApp (Evolution API)
# ---------------------------------------------------------------------------

def _build_whatsapp_text(rows: list[dict], summary: dict) -> str:
    data_fmt = datetime.strptime(summary["data_ref"], "%Y-%m-%d").strftime("%d/%m/%Y") if summary["data_ref"] else summary["data_ref"]

    lines = [
        f"📊 *Relatório Comercial - {data_fmt}*",
        f"Mês: {summary['mes_vendas']}",
        "",
        f"👥 Total de vendedores: *{summary['total_vendedores']}*",
        f"✅ Atingiram a meta: *{summary['atingiram']}* ({fmt_pct(summary['pct_atingiu'])})",
        f"💰 Projeção total: *{fmt_brl(summary['projecao_total'])}*",
        f"🎯 Meta mensal total: *{fmt_brl(summary['meta_mensal_total'])}*",
        f"📈 % Global atingido: *{fmt_pct(summary['pct_global'])}*",
        "",
    ]

    equipes: dict[str, list] = {}
    for r in rows:
        equipes.setdefault(r.get("equipe", "—"), []).append(r)

    icons = {"ATINGIU": "✅", "QUASE": "⚠️", "ABAIXO": "❌"}
    for equipe, membros in equipes.items():
        lines.append(f"*{equipe}*")
        for r in membros:
            icon = icons.get(r.get("status_meta", ""), "•")
            lines.append(
                f"  {icon} {r.get('vendedor','')} — {fmt_pct(r.get('perc_meta_mensal'))} da meta mensal"
            )
        lines.append("")

    return "\n".join(lines)


def send_whatsapp(rows: list[dict], summary: dict) -> None:
    api_url = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
    api_key = os.environ.get("EVOLUTION_API_KEY", "")
    instance = os.environ.get("EVOLUTION_INSTANCE", "")
    numbers_raw = os.environ.get("WHATSAPP_NUMBERS", "")
    numbers = [n.strip() for n in numbers_raw.split(",") if n.strip()]

    if not (api_url and numbers):
        log.error("Configuração WhatsApp incompleta — verifique EVOLUTION_API_URL e WHATSAPP_NUMBERS.")
        return

    text = _build_whatsapp_text(rows, summary)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["apikey"] = api_key

    endpoint = f"{api_url}/message/sendText/{instance}" if instance else f"{api_url}/message/sendText"

    for number in numbers:
        payload = {"number": number, "textMessage": {"text": text}}
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            log.info("WhatsApp enviado para %s", number)
        except Exception as exc:
            log.error("Falha ao enviar WhatsApp para %s: %s", number, exc)


# ---------------------------------------------------------------------------
# CLI / Main
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Gerador de Relatório Comercial Diário")
    parser.add_argument("--date", metavar="YYYY-MM-DD", help="Data específica para filtrar (padrão: hoje em Brasília)")
    parser.add_argument("--html-only", action="store_true", help="Gera apenas o HTML, sem enviar e-mail ou WhatsApp")
    parser.add_argument("--output", metavar="FILE", default="output/relatorio_diario.html", help="Caminho do arquivo HTML gerado")
    return parser.parse_args()


def main():
    args = parse_args()

    log.info("=== Relatório Comercial Diário ===")

    try:
        rows = fetch_relatorio(data_filtro=args.date)
    except Exception as exc:
        log.error("Erro ao buscar dados do Supabase: %s", exc)
        sys.exit(1)

    if not rows:
        log.error("Nenhum dado retornado para a data solicitada.")
        sys.exit(1)

    summary = build_summary(rows)
    log.info(
        "Resumo: %d vendedores, %d atingiram meta (%.1f%%), projeção total %s",
        summary["total_vendedores"],
        summary["atingiram"],
        summary["pct_atingiu"],
        fmt_brl(summary["projecao_total"]),
    )

    html = build_html(rows, summary)

    output_path = args.output
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    log.info("HTML salvo em: %s", output_path)

    if args.html_only:
        log.info("Modo --html-only: envios ignorados.")
        return

    send_email(html, summary)
    send_whatsapp(rows, summary)

    log.info("=== Concluído ===")


# ---------------------------------------------------------------------------
# Modo de teste
# ---------------------------------------------------------------------------

def rodar_teste() -> None:
    """Busca dados reais, gera relatorio_teste.html e envia para TEST_EMAIL."""
    log.info("=== Modo de Teste ===")

    test_email = os.environ.get("TEST_EMAIL", "").strip()

    try:
        rows = fetch_relatorio()
    except Exception as exc:
        log.error("Erro ao buscar dados do Supabase: %s", exc)
        sys.exit(1)

    if not rows:
        log.error("Nenhum dado retornado para a data atual.")
        sys.exit(1)

    summary = build_summary(rows)
    html = build_html(rows, summary)

    os.makedirs("output", exist_ok=True)
    output_path = "output/relatorio_teste.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML salvo em {output_path}")

    if test_email:
        send_email(html, summary, recipients_override=[test_email])
        print(f"✅ E-mail enviado para {test_email}")
    else:
        print("⚠️  TEST_EMAIL não configurado no .env — e-mail ignorado.")

    log.info("=== Teste Concluído ===")


if __name__ == "__main__":
    main()
