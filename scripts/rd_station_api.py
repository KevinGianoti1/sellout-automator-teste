import requests
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Mapeamento fixo de funis por tipo
FUNIS_COMERCIAL = {
    "Pyramid Clientes Semanal": "66d74ce07d2f800014cb0041",
    "Pyramid Clientes Inativos": "67978f4103af500014a9096d",
    "Funil de Campanhas": "67d98c202c2b70001ac19d52",
    "GTFix Clientes Ativos": "69b9c0b58bfbb00013cff1c3",
}
FUNIS_MARKETING = {
    "Funil de Clientes Novos": "67a0f6fe0e4c890018795f0f",
}
TODOS_FUNIS = {**FUNIS_COMERCIAL, **FUNIS_MARKETING}


def _periodo_3_meses() -> tuple:
    hoje = datetime.now()
    inicio = (hoje - timedelta(days=60)).strftime("%Y-%m-%d")
    fim = hoje.strftime("%Y-%m-%d")
    return inicio, fim


class RDStationAPI:
    """Integracao com a API do RD Station CRM."""

    BASE_URL = "https://crm.rdstation.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict = None, retries: int = 6) -> dict:
        params = params or {}
        params["token"] = self.api_key
        for attempt in range(retries):
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/{endpoint}", params=params, timeout=60
                )
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                wait = min(2 ** attempt, 30)
                print(f"   Timeout/conexao — aguardando {wait}s...")
                time.sleep(wait)
                continue
            if response.status_code == 429:
                wait = min(2 ** attempt, 60)
                print(f"   Rate limit — aguardando {wait}s...")
                time.sleep(wait)
                continue
            response.raise_for_status()
            time.sleep(0.5)
            return response.json()
        response.raise_for_status()
        return {}

    def _paginar_deals(self, filtros: dict, limit: int = 50) -> List[Dict]:
        """Pagina todos os deals com limit por pagina e retorna lista completa."""
        deals = []
        next_page = None
        while True:
            params = dict(filtros)
            params["limit"] = limit
            if next_page:
                params["page"] = next_page
            data = self._get("deals", params)
            deals.extend(data.get("deals", []))
            if not data.get("has_more") or not data.get("next_page"):
                break
            next_page = data["next_page"]
        return deals

    # ===== SNAPSHOT (estagios) =====

    def get_pipelines(self) -> List[Dict]:
        return self._get("deal_pipelines")

    def get_all_deals_by_stage(self) -> Dict[str, Dict[str, int]]:
        """Snapshot de TODOS os funis: contagem de leads abertos por estagio."""
        pipelines = self.get_pipelines()
        result = {}
        for pipeline in pipelines:
            name = pipeline.get("name", "")
            result[name] = {}
            for stage in pipeline.get("deal_stages", []):
                stage_name = stage.get("name", "")
                count = self._get("deals", {"deal_stage_id": stage.get("id")}).get("total", 0)
                result[name][stage_name] = count
                print(f"   {name} > {stage_name}: {count}")
        return result

    def get_snapshot_por_funis(self, pipeline_ids: Dict[str, str]) -> Dict[str, Dict[str, int]]:
        """Snapshot filtrado: busca estagios apenas dos funis passados."""
        all_pipelines = self.get_pipelines()
        result = {}
        for pipeline in all_pipelines:
            if pipeline.get("id") not in pipeline_ids.values():
                continue
            name = pipeline.get("name", "")
            result[name] = {}
            for stage in pipeline.get("deal_stages", []):
                stage_name = stage.get("name", "")
                count = self._get("deals", {"deal_stage_id": stage.get("id")}).get("total", 0)
                result[name][stage_name] = count
                print(f"   {name} > {stage_name}: {count}")
        return result

    # ===== USUARIOS =====

    def get_users(self) -> List[Dict]:
        return self._get("users").get("users", [])

    # ===== DADOS DE FUNIL (vendedores + finalizados em uma unica passagem) =====

    def get_dados_funil(self, pipeline_ids: Dict[str, str]) -> Dict:
        """
        Pagina TODOS os deals (abertos, ganhos, perdidos) por pipeline e agrupa
        por vendedor no lado do cliente — elimina 1-call-por-usuario.

        3 paginacoes por pipeline (abertos / won / lost) em vez de 12+ calls.
        """
        inicio, fim = _periodo_3_meses()

        em_andamento_map: Dict[str, int] = {}
        ganhos_map: Dict[str, int] = {}
        valor_map: Dict[str, float] = {}
        perdidos_map: Dict[str, int] = {}
        finalizados: Dict[str, Dict] = {}

        all_pipelines = self.get_pipelines()
        stage_map = {}
        for p in all_pipelines:
            if p.get("id") in pipeline_ids.values():
                for s in p.get("deal_stages", []):
                    stage_map[s["id"]] = p.get("name", "")

        print(f"   Em andamento: paginando {len(stage_map)} estagios...")
        for stage_id in stage_map:
            deals_stage = self._paginar_deals({"deal_stage_id": stage_id})
            for deal in deals_stage:
                user = deal.get("user", {}) or {}
                nome = (user.get("name") or "").strip()
                if nome:
                    em_andamento_map[nome] = em_andamento_map.get(nome, 0) + 1

        for pipeline_name, pid in pipeline_ids.items():

            print(f"   [{pipeline_name}] Paginando ganhos...")
            deals_won = self._paginar_deals({
                "deal_pipeline_id": pid,
                "win": "true",
                "closed_at_from": inicio,
                "closed_at_to": fim,
            })
            won_count = len(deals_won)
            won_value = 0.0
            for deal in deals_won:
                user = deal.get("user", {}) or {}
                nome = (user.get("name") or "").strip()
                amt = float(deal.get("amount_total") or 0)
                won_value += amt
                if nome:
                    ganhos_map[nome] = ganhos_map.get(nome, 0) + 1
                    valor_map[nome] = valor_map.get(nome, 0.0) + amt

            print(f"   [{pipeline_name}] Paginando perdidos...")
            deals_lost = self._paginar_deals({
                "deal_pipeline_id": pid,
                "lost": "true",
                "closed_at_from": inicio,
                "closed_at_to": fim,
            })
            lost_count = len(deals_lost)
            for deal in deals_lost:
                user = deal.get("user", {}) or {}
                nome = (user.get("name") or "").strip()
                if nome:
                    perdidos_map[nome] = perdidos_map.get(nome, 0) + 1

            finalizados[pipeline_name] = {
                "won": {"count": won_count, "value": won_value},
                "lost": {"count": lost_count},
            }
            print(f"   {pipeline_name}: {won_count} ganhos | {lost_count} perdidos")

        # Montar lista de vendedores
        todos_nomes = set(em_andamento_map) | set(ganhos_map) | set(perdidos_map)
        vendedores = []
        for nome in todos_nomes:
            ea = em_andamento_map.get(nome, 0)
            g = ganhos_map.get(nome, 0)
            p = perdidos_map.get(nome, 0)
            if ea > 0 or g > 0 or p > 0:
                vendedores.append({
                    "vendedor": nome,
                    "criadas": ea + g + p,
                    "em_andamento": ea,
                    "ganhos_3m": g,
                    "perdidos_3m": p,
                    "valor_ganhos_3m": valor_map.get(nome, 0.0),
                })

        vendedores.sort(key=lambda x: x["criadas"], reverse=True)

        return {"vendedores": vendedores, "finalizados": finalizados}

    # ===== TAXA DE CONVERSAO =====

    def calcular_taxa_conversao(self, snapshot: Dict[str, Dict[str, int]]) -> Dict[str, List[Dict]]:
        """Taxa de conversao entre estagios consecutivos de cada funil."""
        result = {}
        for pipeline_name, stages in snapshot.items():
            stage_list = list(stages.items())
            pipeline_result = []
            for i, (stage_name, count) in enumerate(stage_list):
                if i < len(stage_list) - 1:
                    prox_nome, prox_count = stage_list[i + 1]
                    taxa = round(prox_count / count * 100, 1) if count > 0 else 0.0
                else:
                    prox_nome, prox_count, taxa = None, None, None
                pipeline_result.append({
                    "estagio": stage_name,
                    "count": count,
                    "proximo_estagio": prox_nome,
                    "proximo_count": prox_count,
                    "taxa_pct": taxa,
                })
            result[pipeline_name] = pipeline_result
        return result

    # ===== MOVIMENTACOES =====

    def calculate_movements(self, current: Dict, previous: Dict) -> Dict:
        movements = {}
        for pipeline in set(current.keys()) | set(previous.keys()):
            cur_s = current.get(pipeline, {})
            prev_s = previous.get(pipeline, {})
            for stage in set(cur_s.keys()) | set(prev_s.keys()):
                cur, prev = cur_s.get(stage, 0), prev_s.get(stage, 0)
                if cur != prev:
                    movements.setdefault(pipeline, {})[stage] = {
                        "type": "advancement" if cur > prev else "regression",
                        "change": abs(cur - prev),
                    }
        return movements


def get_rd_station_client(api_key: str = None) -> RDStationAPI:
    if not api_key:
        api_key = os.getenv("RD_STATION_API_KEY")
    if not api_key:
        raise ValueError("RD_STATION_API_KEY nao configurada")
    return RDStationAPI(api_key)
