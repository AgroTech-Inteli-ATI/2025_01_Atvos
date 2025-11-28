from datetime import datetime, timezone
from typing import List, Optional


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Recebe uma string ISO 8601 simples (ex.: 2025-01-01T00:00:00)
    e retorna um datetime normalizado em UTC.
    """
    if not value:
        return None

    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1]

    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return None

    if parsed.tzinfo:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

    return parsed


def format_datetime_for_bigquery(value: datetime) -> str:
    """
    Converte um datetime para o formato aceito pelo TIMESTAMP do BigQuery.
    """
    return value.strftime("%Y-%m-%d %H:%M:%S")


def build_datetime_filters(
    column: str,
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[str]:
    """
    Retorna uma lista de filtros SQL prontos para aplicar em queries.
    """
    filters: List[str] = []

    if start:
        filters.append(
            f"{column} >= TIMESTAMP('{format_datetime_for_bigquery(start)}')"
        )

    if end:
        filters.append(
            f"{column} <= TIMESTAMP('{format_datetime_for_bigquery(end)}')"
        )

    return filters

