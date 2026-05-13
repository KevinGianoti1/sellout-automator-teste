import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
import os
from typing import Dict, Tuple
from jinja2 import Template

def gerar_relatorio_excel(snapshot_data: Dict, movements_data: Dict, filepath: str) -> None:
    """
    Gera relatório Excel com dados de leads e movimentações.

    Args:
        snapshot_data: Dict com snapshot de leads {funnel: {stage: count}}
        movements_data: Dict com movimentações {funnel: {stage: {type: movement_type, change: quantity}}}
        filepath: Caminho para salvar o arquivo Excel
    """
    wb = Workbook()
    wb.remove(wb.active)

    # Configurações de estilo
    header_fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    subheader_fill = PatternFill(start_color="D9E8F5", end_color="D9E8F5", fill_type="solid")
    subheader_font = Font(bold=True, size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")

    # === ABA 1: RESUMO ===
    ws_resumo = wb.create_sheet("Resumo", 0)

    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ws_resumo['A1'] = "RELATÓRIO DE LEADS - RD STATION"
    ws_resumo['A1'].font = Font(bold=True, size=14, color="1F77B4")
    ws_resumo['A2'] = f"Data: {data_geracao}"
    ws_resumo['A2'].font = Font(italic=True, size=10)

    linha = 4

    # KPI Total de Leads
    total_leads = sum(sum(stages.values()) for stages in snapshot_data.values())
    ws_resumo[f'A{linha}'] = "TOTAL DE LEADS:"
    ws_resumo[f'A{linha}'].font = subheader_font
    ws_resumo[f'B{linha}'] = total_leads
    ws_resumo[f'B{linha}'].font = Font(bold=True, size=12, color="006100")
    linha += 2

    # Por funil
    ws_resumo[f'A{linha}'] = "DISTRIBUIÇÃO POR FUNIL:"
    ws_resumo[f'A{linha}'].font = subheader_font
    linha += 1

    col_headers = ['Funil', 'Total de Leads']
    for col_idx, header in enumerate(col_headers, 1):
        cell = ws_resumo.cell(row=linha, column=col_idx)
        cell.value = header
        cell.fill = subheader_fill
        cell.font = subheader_font
        cell.border = border
        cell.alignment = center_align

    linha += 1

    for funnel_name, stages in sorted(snapshot_data.items()):
        total_funnel = sum(stages.values())
        ws_resumo.cell(row=linha, column=1).value = funnel_name
        ws_resumo.cell(row=linha, column=2).value = total_funnel
        for col in [1, 2]:
            ws_resumo.cell(row=linha, column=col).border = border
            ws_resumo.cell(row=linha, column=col).alignment = center_align
        linha += 1

    # === ABA 2: LEADS POR FUNIL ===
    ws_leads = wb.create_sheet("Leads por Funil", 1)
    ws_leads['A1'] = "LEADS POR ESTÁGIO DO FUNIL"
    ws_leads['A1'].font = Font(bold=True, size=14, color="1F77B4")

    linha = 3
    for funnel_name, stages in sorted(snapshot_data.items()):
        ws_leads[f'A{linha}'] = f"📊 {funnel_name.upper()}"
        ws_leads[f'A{linha}'].font = subheader_font
        ws_leads[f'A{linha}'].fill = subheader_fill
        linha += 1

        # Cabeçalho da tabela
        headers = ['Estágio', 'Quantidade de Leads']
        for col_idx, header in enumerate(headers, 1):
            cell = ws_leads.cell(row=linha, column=col_idx)
            cell.value = header
            cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
            cell.font = Font(bold=True)
            cell.border = border
            cell.alignment = center_align

        linha += 1

        # Dados dos estágios
        for stage_name, count in sorted(stages.items()):
            ws_leads.cell(row=linha, column=1).value = stage_name
            ws_leads.cell(row=linha, column=2).value = count
            for col in [1, 2]:
                ws_leads.cell(row=linha, column=col).border = border
                ws_leads.cell(row=linha, column=col).alignment = center_align
            linha += 1

        linha += 1

    # === ABA 3: MOVIMENTAÇÕES ===
    ws_mov = wb.create_sheet("Movimentações", 2)
    ws_mov['A1'] = "MOVIMENTAÇÕES DE LEADS"
    ws_mov['A1'].font = Font(bold=True, size=14, color="1F77B4")

    linha = 3
    headers = ['Funil', 'Estágio', 'Tipo', 'Quantidade']
    for col_idx, header in enumerate(headers, 1):
        cell = ws_mov.cell(row=linha, column=col_idx)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = center_align

    linha += 1

    has_movements = False
    for funnel_name, stages in sorted(movements_data.items()):
        for stage_name, movement in sorted(stages.items()):
            has_movements = True
            movement_type = movement.get('type', 'unknown')
            quantity = movement.get('change', movement.get('count', 0))

            # Traduzir tipos
            type_map = {
                'advancement': '📈 Avanço',
                'regression': '📉 Retrocesso',
                'exit': '❌ Saída'
            }
            tipo_display = type_map.get(movement_type, movement_type)

            # Colorir por tipo
            if movement_type == 'advancement':
                color_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            elif movement_type == 'regression':
                color_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            else:
                color_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

            ws_mov.cell(row=linha, column=1).value = funnel_name
            ws_mov.cell(row=linha, column=2).value = stage_name
            ws_mov.cell(row=linha, column=3).value = tipo_display
            ws_mov.cell(row=linha, column=4).value = quantity

            for col in range(1, 5):
                cell = ws_mov.cell(row=linha, column=col)
                cell.fill = color_fill
                cell.border = border
                cell.alignment = center_align

            linha += 1

    if not has_movements:
        ws_mov['A4'] = "Nenhuma movimentação detectada"
        ws_mov['A4'].font = Font(italic=True, color="999999")

    # Ajustar largura das colunas
    for ws in [ws_resumo, ws_leads, ws_mov]:
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)

def gerar_email_html(snapshot_data: Dict, movements_data: Dict) -> str:
    """
    Gera HTML para envio de email com resumo de leads.

    Args:
        snapshot_data: Dict com snapshot de leads
        movements_data: Dict com movimentações

    Returns:
        String com HTML do email
    """
    total_leads = sum(sum(stages.values()) for stages in snapshot_data.values())

    template_str = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header {
                background-color: #1f77b4;
                color: white;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 0;
                font-size: 28px;
            }
            .header p {
                margin: 5px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }
            .kpi {
                display: inline-block;
                background-color: #f0f0f0;
                padding: 15px 25px;
                margin: 10px 5px;
                border-radius: 5px;
                text-align: center;
                border-left: 4px solid #1f77b4;
            }
            .kpi .number {
                font-size: 32px;
                font-weight: bold;
                color: #1f77b4;
            }
            .kpi .label {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            .section {
                margin: 20px 0;
            }
            .section-title {
                background-color: #1f77b4;
                color: white;
                padding: 10px 15px;
                border-radius: 3px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th {
                background-color: #e7e6e6;
                padding: 10px;
                text-align: left;
                font-weight: bold;
                border-bottom: 2px solid #1f77b4;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background-color: #f9f9f9;
            }
            .advancement { color: green; }
            .regression { color: red; }
            .exit { color: orange; }
            .footer {
                text-align: center;
                color: #999;
                font-size: 12px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Relatório de Leads - RD Station</h1>
                <p>{{ data_geracao }}</p>
            </div>

            <div style="text-align: center;">
                <div class="kpi">
                    <div class="number">{{ total_leads }}</div>
                    <div class="label">Total de Leads</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">📈 Distribuição por Funil</div>
                <table>
                    <thead>
                        <tr>
                            <th>Funil</th>
                            <th style="text-align: center;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for funnel_name, stages in snapshot_data.items() | sort %}
                        <tr>
                            <td>{{ funnel_name }}</td>
                            <td style="text-align: center;"><strong>{{ stages.values() | sum }}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="section-title">🎯 Leads por Estágio</div>
                {% for funnel_name, stages in snapshot_data.items() | sort %}
                <h4>{{ funnel_name }}</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Estágio</th>
                            <th style="text-align: center;">Quantidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for stage_name, count in stages.items() | sort %}
                        <tr>
                            <td>{{ stage_name }}</td>
                            <td style="text-align: center;"><strong>{{ count }}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endfor %}
            </div>

            {% if movements_data %}
            <div class="section">
                <div class="section-title">⚡ Movimentações Detectadas</div>
                <table>
                    <thead>
                        <tr>
                            <th>Funil</th>
                            <th>Estágio</th>
                            <th>Tipo</th>
                            <th style="text-align: center;">Quantidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for funnel_name, stages in movements_data.items() | sort %}
                            {% for stage_name, movement in stages.items() | sort %}
                            <tr>
                                <td>{{ funnel_name }}</td>
                                <td>{{ stage_name }}</td>
                                <td class="{% if movement.type == 'advancement' %}advancement{% elif movement.type == 'regression' %}regression{% else %}exit{% endif %}">
                                    {% if movement.type == 'advancement' %}
                                        📈 Avanço
                                    {% elif movement.type == 'regression' %}
                                        📉 Retrocesso
                                    {% else %}
                                        ❌ Saída
                                    {% endif %}
                                </td>
                                <td style="text-align: center;"><strong>{{ movement.change or movement.count }}</strong></td>
                            </tr>
                            {% endfor %}
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <div class="footer">
                <p>Relatório gerado automaticamente pelo Sistema de Automação - RD Station</p>
                <p>Dúvidas? Entre em contato com o time de análise de vendas</p>
            </div>
        </div>
    </body>
    </html>
    """

    template = Template(template_str)
    html = template.render(
        data_geracao=datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        total_leads=total_leads,
        snapshot_data=snapshot_data,
        movements_data=movements_data
    )

    return html
