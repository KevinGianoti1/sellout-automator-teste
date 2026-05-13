import requests
import os
from datetime import datetime
from typing import Dict, List


class RDStationAPI:
    """Integração com a API do RD Station CRM para gerenciar leads e funis."""

    BASE_URL = "https://crm.rdstation.com/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Faz GET autenticado (token no query param)."""
        params = params or {}
        params['token'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_pipelines(self) -> List[Dict]:
        """
        Retorna lista de funis (deal_pipelines) do RD Station CRM.

        Returns:
            Lista de funis com seus estágios
        """
        return self._get("deal_pipelines")

    def get_deals(self, page: str = None, deal_stage_id: str = None) -> Dict:
        """
        Retorna deals (negócios/leads) do CRM.

        Args:
            page: Token de paginação para próxima página
            deal_stage_id: Filtrar por estágio específico

        Returns:
            Dict com total, has_more, next_page e lista de deals
        """
        params = {}
        if page:
            params['page'] = page
        if deal_stage_id:
            params['deal_stage_id'] = deal_stage_id
        return self._get("deals", params=params)

    def get_count_by_stage(self, stage_id: str) -> int:
        """
        Retorna a contagem total de deals em um estágio específico (sem paginar).

        Args:
            stage_id: ID do estágio

        Returns:
            Total de deals no estágio
        """
        data = self._get("deals", params={'deal_stage_id': stage_id, 'page_size': 1})
        return data.get('total', 0)

    def get_all_deals_by_stage(self) -> Dict[str, Dict[str, int]]:
        """
        Retorna contagem de deals agrupados por funil e estágio.
        Usa filtro por estágio para eficiência - sem paginação de todos os deals.

        Returns:
            Dict: {pipeline_name: {stage_name: count}}
        """
        pipelines = self.get_pipelines()
        result = {}

        for pipeline in pipelines:
            pipeline_name = pipeline.get('name', 'Funil sem nome')
            result[pipeline_name] = {}

            for stage in pipeline.get('deal_stages', []):
                stage_id = stage.get('id')
                stage_name = stage.get('name', 'Estágio sem nome')
                count = self.get_count_by_stage(stage_id)
                result[pipeline_name][stage_name] = count
                print(f"   {pipeline_name} > {stage_name}: {count} leads")

        return result

    def calculate_movements(self, current: Dict[str, Dict[str, int]],
                             previous: Dict[str, Dict[str, int]]) -> Dict:
        """
        Calcula movimentações de leads entre dois snapshots.

        Args:
            current: Snapshot atual {pipeline: {stage: count}}
            previous: Snapshot anterior {pipeline: {stage: count}}

        Returns:
            Dict com avanços, retrocessos e saídas por estágio
        """
        movements = {}

        all_pipelines = set(current.keys()) | set(previous.keys())

        for pipeline in all_pipelines:
            current_stages = current.get(pipeline, {})
            prev_stages = previous.get(pipeline, {})
            all_stages = set(current_stages.keys()) | set(prev_stages.keys())

            for stage in all_stages:
                cur = current_stages.get(stage, 0)
                prev = prev_stages.get(stage, 0)

                if cur != prev:
                    if pipeline not in movements:
                        movements[pipeline] = {}

                    mov_type = 'advancement' if cur > prev else 'regression'
                    movements[pipeline][stage] = {
                        'type': mov_type,
                        'change': abs(cur - prev)
                    }

        return movements


def get_rd_station_client(api_key: str = None) -> RDStationAPI:
    """
    Factory para criar cliente RD Station.

    Args:
        api_key: API Key. Se não fornecida, lê de RD_STATION_API_KEY

    Returns:
        Instância de RDStationAPI
    """
    if not api_key:
        api_key = os.getenv('RD_STATION_API_KEY')

    if not api_key:
        raise ValueError("RD_STATION_API_KEY não configurada")

    return RDStationAPI(api_key)
