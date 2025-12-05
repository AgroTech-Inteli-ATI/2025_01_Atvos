import os
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Iterable, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Travel Cost Dashboard", layout="wide")

DEFAULT_BASE_URL = os.getenv("AGRO_API_BASE_URL", "https://src-api-1008983555717.europe-west1.run.app/api")
DEFAULT_TOKEN = os.getenv("AGRO_API_TOKEN", "")
PERIOD_LABELS = {
    "month": "Mensal",
    "week": "Semanal",
    "day": "Diario",
}
PERIOD_CHOICES = list(PERIOD_LABELS.keys())
COMMON_COST_COLUMNS = (
    "bill.total_cost",
    "travel_cost",
    "total_cost",
    "cost",
    "bill_total_cost",
    "cost_value",
)

MOCK_UNITS = [
    {"id": 1, "name": "Fazenda Norte", "description": "Operação norte"},
    {"id": 2, "name": "Fazenda Sul", "description": "Operação sul"},
    {"id": 3, "name": "Centro Logístico", "description": "Hub de distribuição"},
]

MOCK_TRAVEL_TEMPLATES = [
    {
        "id": "T-101",
        "days_ago": 3,
        "time": "08:30",
        "license_plate": "ABC1D23",
        "asset_description": "Caminhão Graneleiro",
        "register_number": "REG-001",
        "garage_name": "Base Norte",
        "full_distance": 198.4,
        "unit_id": 1,
        "unit_name": "Fazenda Norte",
        "total_cost": 3365.55,
    },
    {
        "id": "T-102",
        "days_ago": 9,
        "time": "06:45",
        "license_plate": "DEF2G34",
        "asset_description": "Carreta Granel",
        "register_number": "REG-002",
        "garage_name": "Base Norte",
        "full_distance": 142.7,
        "unit_id": 1,
        "unit_name": "Fazenda Norte",
        "total_cost": 2540.10,
    },
    {
        "id": "T-201",
        "days_ago": 15,
        "time": "09:10",
        "license_plate": "GHI3J45",
        "asset_description": "Caminhão Tanque",
        "register_number": "REG-010",
        "garage_name": "Base Sul",
        "full_distance": 205.3,
        "unit_id": 2,
        "unit_name": "Fazenda Sul",
        "total_cost": 3387.80,
    },
    {
        "id": "T-202",
        "days_ago": 24,
        "time": "13:20",
        "license_plate": "JKL4M56",
        "asset_description": "Bitrem",
        "register_number": "REG-011",
        "garage_name": "Base Sul",
        "full_distance": 167.9,
        "unit_id": 2,
        "unit_name": "Fazenda Sul",
        "total_cost": 2895.60,
    },
    {
        "id": "T-301",
        "days_ago": 28,
        "time": "07:55",
        "license_plate": "MNO5P67",
        "asset_description": "Caminhão Baú",
        "register_number": "REG-020",
        "garage_name": "Centro Oeste",
        "full_distance": 123.4,
        "unit_id": 3,
        "unit_name": "Centro Logístico",
        "total_cost": 2150.90,
    },
    {
        "id": "T-302",
        "days_ago": 38,
        "time": "11:15",
        "license_plate": "PQR6S78",
        "asset_description": "Prancha",
        "register_number": "REG-021",
        "garage_name": "Centro Oeste",
        "full_distance": 198.6,
        "unit_id": 3,
        "unit_name": "Centro Logístico",
        "total_cost": 3625.45,
    },
    {
        "id": "T-303",
        "days_ago": 52,
        "time": "05:40",
        "license_plate": "STU7V89",
        "asset_description": "Truck",
        "register_number": "REG-022",
        "garage_name": "Centro Oeste",
        "full_distance": 98.2,
        "unit_id": 3,
        "unit_name": "Centro Logístico",
        "total_cost": 1740.30,
    },
    {
        "id": "T-304",
        "days_ago": 64,
        "time": "15:05",
        "license_plate": "VWX8Y90",
        "asset_description": "Caminhão Caçamba",
        "register_number": "REG-023",
        "garage_name": "Centro Oeste",
        "full_distance": 210.8,
        "unit_id": 3,
        "unit_name": "Centro Logístico",
        "total_cost": 3755.15,
    },
]

MOCK_BILL_TEMPLATES = [
    {
        "id": "B-101",
        "travel_id": "T-101",
        "days_ago": 2,
        "time": "20:15",
        "fix_cost": 1550.00,
        "variable_km": 9.15,
    },
    {
        "id": "B-102",
        "travel_id": "T-102",
        "days_ago": 8,
        "time": "18:40",
        "fix_cost": 1350.00,
        "variable_km": 8.35,
    },
    {
        "id": "B-201",
        "travel_id": "T-201",
        "days_ago": 14,
        "time": "21:00",
        "fix_cost": 1525.00,
        "variable_km": 9.12,
    },
    {
        "id": "B-202",
        "travel_id": "T-202",
        "days_ago": 23,
        "time": "22:10",
        "fix_cost": 1400.00,
        "variable_km": 8.90,
    },
    {
        "id": "B-301",
        "travel_id": "T-301",
        "days_ago": 27,
        "time": "17:30",
        "fix_cost": 1200.00,
        "variable_km": 7.70,
    },
    {
        "id": "B-302",
        "travel_id": "T-302",
        "days_ago": 37,
        "time": "23:00",
        "fix_cost": 1500.00,
        "variable_km": 10.70,
    },
    {
        "id": "B-303",
        "travel_id": "T-303",
        "days_ago": 51,
        "time": "12:45",
        "fix_cost": 1100.00,
        "variable_km": 6.50,
    },
    {
        "id": "B-304",
        "travel_id": "T-304",
        "days_ago": 63,
        "time": "23:40",
        "fix_cost": 1550.00,
        "variable_km": 10.50,
    },
]


def get_mock_units_df() -> pd.DataFrame:
    return pd.DataFrame(MOCK_UNITS)


def _mock_datetime(days_ago: int, time_str: str, reference: date) -> datetime:
    hour, minute = [int(part) for part in time_str.split(":")]
    anchor = datetime.combine(reference, time(hour=hour, minute=minute))
    return anchor - timedelta(days=days_ago)


def get_mock_travels_df(
    unit_id: Optional[str],
    start_date: date,
    end_date: date,
    limit: int,
) -> pd.DataFrame:
    records = []
    for template in MOCK_TRAVEL_TEMPLATES:
        travel_dt = _mock_datetime(template["days_ago"], template["time"], end_date)
        if not (start_date <= travel_dt.date() <= end_date):
            continue
        if unit_id is not None and str(template["unit_id"]) != str(unit_id):
            continue

        record = {
            "id": template["id"],
            "datetime": travel_dt.isoformat(),
            "license_plate": template["license_plate"],
            "asset_description": template["asset_description"],
            "register_number": template["register_number"],
            "garage_name": template["garage_name"],
            "full_distance": template["full_distance"],
            "unit_id": str(template["unit_id"]),
            "unit_name": template["unit_name"],
            "bill.total_cost": template["total_cost"],
            "total_cost": template["total_cost"],
        }
        records.append(record)

    if not records:
        return pd.DataFrame()

    records.sort(key=lambda item: item["datetime"], reverse=True)
    if limit:
        records = records[:limit]

    return pd.DataFrame(records)


def get_mock_bills_df(travel_ids: Iterable[Any], end_date: date) -> pd.DataFrame:
    ids = {str(tid) for tid in travel_ids if tid is not None}
    records = []
    for template in MOCK_BILL_TEMPLATES:
        if template["travel_id"] not in ids and ids:
            continue
        bill_dt = _mock_datetime(template["days_ago"], template["time"], end_date)
        record = {
            "id": template["id"],
            "travel_id": template["travel_id"],
            "datetime": bill_dt.isoformat(),
            "fix_cost": template["fix_cost"],
            "variable_km": template["variable_km"],
        }
        records.append(record)

    if not records:
        return pd.DataFrame()

    for record in records:
        linked_travel = next((t for t in MOCK_TRAVEL_TEMPLATES if t["id"] == record["travel_id"]), None)
        if linked_travel:
            distance = linked_travel["full_distance"]
            record["total_cost"] = record["fix_cost"] + record["variable_km"] * distance
        else:
            record["total_cost"] = record["fix_cost"]

    return pd.DataFrame(records)


def build_mock_summary(travels_df: pd.DataFrame) -> Dict[str, float]:
    if travels_df.empty:
        return {
            "total_distance_km": 0.0,
            "total_cost": 0.0,
            "total_travels": 0,
            "avg_cost_per_travel": 0.0,
            "avg_distance_per_travel": 0.0,
        }

    tmp = travels_df.copy()
    tmp["full_distance"] = ensure_numeric(tmp, "full_distance").fillna(0)
    cost_col = first_valid_column(tmp, COMMON_COST_COLUMNS)
    tmp["cost_value"] = ensure_numeric(tmp, cost_col).fillna(0) if cost_col else 0

    total_travels = int(tmp.shape[0])
    total_distance = float(tmp["full_distance"].sum())
    total_cost = float(tmp["cost_value"].sum())

    avg_cost = total_cost / total_travels if total_travels else 0.0
    avg_distance = total_distance / total_travels if total_travels else 0.0

    return {
        "total_distance_km": total_distance,
        "total_cost": total_cost,
        "total_travels": total_travels,
        "avg_cost_per_travel": avg_cost,
        "avg_distance_per_travel": avg_distance,
    }


def build_mock_cost_payload(
    travels_df: pd.DataFrame,
    period: str,
    period_limit: int,
) -> Optional[Dict[str, Any]]:
    if travels_df.empty:
        return None

    tmp = travels_df.copy()
    tmp["datetime"] = pd.to_datetime(tmp["datetime"], errors="coerce")
    tmp = tmp.dropna(subset=["datetime"])
    if tmp.empty:
        return None

    cost_df = build_cost_evolution_from_travels(tmp, period)
    if cost_df.empty:
        return None

    if period_limit:
        cost_df = cost_df.tail(period_limit)

    return {"status": "ok", "data": cost_df.to_dict(orient="records")}


@st.cache_data(ttl=300)
def cached_get(
    url: str,
    params_tuple: Tuple[Tuple[str, str], ...],
    headers_tuple: Tuple[Tuple[str, str], ...],
) -> Dict[str, Any]:
    """Executa requests.get com cache simples."""
    params = {k: v for k, v in params_tuple}
    headers = {k: v for k, v in headers_tuple}
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def call_api(
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Chama a API do Agro-Server com tratamento simples de erros."""
    if not base_url:
        return None

    cleaned_params = {k: v for k, v in (params or {}).items() if v not in (None, "", [])}
    params_tuple = tuple(sorted((k, str(v)) for k, v in cleaned_params.items()))

    headers: Dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers_tuple = tuple(sorted(headers.items()))

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    try:
        return cached_get(url, params_tuple, headers_tuple)
    except requests.HTTPError as exc:
        detail = ""
        if exc.response is not None:
            try:
                body = exc.response.json()
                if isinstance(body, dict):
                    detail = body.get("erro") or body.get("detail") or str(body)
                else:
                    detail = str(body)
            except Exception:
                detail = exc.response.text
        st.error(f"API {path} retornou {exc.response.status_code}: {detail}")
    except requests.RequestException as exc:
        st.error(f"Falha ao acessar {path}: {exc}")
    except Exception as exc:
        st.error(f"Erro inesperado ao acessar {path}: {exc}")
    return None


def extract_data(payload: Optional[Any]) -> Optional[Any]:
    if payload is None:
        return None
    if isinstance(payload, dict):
        if "data" in payload and payload["data"] not in (None, []):
            return payload["data"]
        if "results" in payload:
            return payload["results"]
    return payload


def extract_first_dict(payload: Optional[Any]) -> Optional[Dict[str, Any]]:
    data = extract_data(payload)
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                return item
    if isinstance(payload, dict):
        return payload
    return None


def build_dataframe(payload: Optional[Any]) -> pd.DataFrame:
    data = extract_data(payload)
    if data is None:
        return pd.DataFrame()
    if isinstance(data, dict):
        nested = data.get("data") or data.get("results")
        if nested is not None:
            data = nested
    if data is None:
        return pd.DataFrame()
    if not isinstance(data, list):
        data = [data]
    if not data:
        return pd.DataFrame()
    return pd.json_normalize(data, sep=".")


def ensure_numeric(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce")


def safe_extract(source: Optional[Dict[str, Any]], keys: Tuple[str, ...]) -> Optional[Any]:
    if not isinstance(source, dict):
        return None
    for key in keys:
        value = source.get(key)
        if value not in (None, "", []):
            return value
    return None


def coerce_float(value: Any) -> Optional[float]:
    if value in (None, "", []):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def coerce_int(value: Any) -> Optional[int]:
    if value in (None, "", []):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def format_currency(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_decimal(value: Optional[float], decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    formatted = f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def format_number(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value:,.0f}".replace(",", ".")


def first_valid_column(df: pd.DataFrame, candidates: Tuple[str, ...]) -> Optional[str]:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def first_present_series(df: pd.DataFrame, candidates: Tuple[str, ...]) -> Optional[pd.Series]:
    for column in candidates:
        if column in df.columns:
            return df[column]
    return None


def compute_metrics(
    summary: Optional[Dict[str, Any]],
    travels_df: pd.DataFrame,
    bills_df: Optional[pd.DataFrame],
) -> Dict[str, Optional[float]]:
    metrics: Dict[str, Optional[float]] = {
        "total_travels": None,
        "total_distance": None,
        "total_cost": None,
        "avg_cost_per_travel": None,
        "avg_distance_per_travel": None,
    }

    total_travels = coerce_int(
        safe_extract(summary, ("total_travels", "travels", "count", "total_viagens"))
    )
    if total_travels is None and not travels_df.empty:
        total_travels = int(travels_df.shape[0])
    metrics["total_travels"] = total_travels

    total_distance = coerce_float(
        safe_extract(summary, ("total_distance_km", "total_km", "distance_total", "distance"))
    )
    if total_distance is None and "full_distance" in travels_df.columns:
        distance_series = ensure_numeric(travels_df, "full_distance")
        if distance_series.notna().any():
            total_distance = distance_series.sum()
    metrics["total_distance"] = total_distance

    total_cost = coerce_float(safe_extract(summary, ("total_cost", "cost_total")))
    if total_cost is None and not travels_df.empty:
        cost_col = first_valid_column(travels_df, COMMON_COST_COLUMNS)
        if cost_col:
            values = ensure_numeric(travels_df, cost_col)
            if values.notna().any():
                total_cost = values.sum()
    if total_cost is None and bills_df is not None and not bills_df.empty:
        cost_col = first_valid_column(bills_df, ("total_cost", "bill.total_cost", "cost"))
        if cost_col:
            values = ensure_numeric(bills_df, cost_col)
            if values.notna().any():
                total_cost = values.sum()
        elif {
            "fix_cost",
            "variable_km",
            "travel_id",
        }.issubset(set(bills_df.columns)) and not travels_df.empty:
            fix_series = ensure_numeric(bills_df, "fix_cost").fillna(0)
            variable_series = ensure_numeric(bills_df, "variable_km").fillna(0)
            if "id" in travels_df.columns and "full_distance" in travels_df.columns:
                id_map = dict(
                    zip(
                        travels_df["id"].astype(str),
                        ensure_numeric(travels_df, "full_distance").fillna(0),
                    )
                )
                travel_distances = bills_df["travel_id"].astype(str).map(id_map).fillna(0)
                total_cost = (fix_series + variable_series * travel_distances).sum()
    metrics["total_cost"] = total_cost

    avg_cost = coerce_float(safe_extract(summary, ("avg_cost_per_travel", "avg_cost")))
    if avg_cost is None and total_cost is not None and total_travels:
        avg_cost = total_cost / total_travels
    metrics["avg_cost_per_travel"] = avg_cost

    avg_distance = coerce_float(
        safe_extract(summary, ("avg_distance_per_travel", "avg_distance"))
    )
    if avg_distance is None and total_distance is not None and total_travels:
        avg_distance = total_distance / total_travels
    metrics["avg_distance_per_travel"] = avg_distance

    return metrics


def build_cost_evolution_from_travels(travels_df: pd.DataFrame, period: str) -> pd.DataFrame:
    if travels_df.empty or "datetime" not in travels_df.columns:
        return pd.DataFrame()
    tmp = travels_df.copy()
    tmp["datetime"] = pd.to_datetime(tmp["datetime"], errors="coerce")
    tmp = tmp.dropna(subset=["datetime"])
    if tmp.empty:
        return pd.DataFrame()

    cost_col = first_valid_column(tmp, COMMON_COST_COLUMNS)
    if not cost_col:
        return pd.DataFrame()

    tmp["cost_value"] = ensure_numeric(tmp, cost_col).fillna(0)
    tmp["distance_value"] = ensure_numeric(tmp, "full_distance").fillna(0)
    travel_key = "id" if "id" in tmp.columns else "datetime"

    if period == "day":
        tmp["period_start"] = tmp["datetime"].dt.floor("D")
        tmp["period_label"] = tmp["period_start"].dt.strftime("%Y-%m-%d")
    elif period == "week":
        period_index = tmp["datetime"].dt.to_period("W-MON")
        tmp["period_start"] = period_index.dt.to_timestamp()
        tmp["period_label"] = tmp["period_start"].dt.strftime("Sem %W/%Y")
    else:
        tmp["period_start"] = tmp["datetime"].dt.to_period("M").dt.to_timestamp()
        tmp["period_label"] = tmp["period_start"].dt.strftime("%Y-%m")

    grouped = (
        tmp.groupby(["period_start", "period_label"], as_index=False)
        .agg(
            total_cost=("cost_value", "sum"),
            total_distance=("distance_value", "sum"),
            total_travels=(travel_key, "count"),
        )
        .sort_values("period_start")
    )
    return grouped


def render_summary_cards(metrics: Dict[str, Optional[float]]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Custo total", format_currency(metrics.get("total_cost")))
    col2.metric("Total de viagens", format_number(metrics.get("total_travels")))
    col3.metric("Distancia total (km)", format_decimal(metrics.get("total_distance")))
    col4.metric("Ticket medio", format_currency(metrics.get("avg_cost_per_travel")))
    avg_dist = metrics.get("avg_distance_per_travel")
    if avg_dist is not None:
        st.caption(f"Distancia media por viagem: {format_decimal(avg_dist)} km")


def render_cost_chart(
    cost_payload: Optional[Dict[str, Any]],
    travels_df: pd.DataFrame,
    period: str,
) -> None:
    cost_df = build_dataframe(cost_payload)
    if not cost_df.empty:
        if "period_label" not in cost_df.columns:
            if "period_full_date" in cost_df.columns:
                cost_df["period_label"] = cost_df["period_full_date"]
            elif "period" in cost_df.columns:
                cost_df["period_label"] = cost_df["period"]
            else:
                cost_df["period_label"] = [f"{i+1}" for i in range(len(cost_df))]
        cost_df["total_cost"] = ensure_numeric(cost_df, "total_cost")
        if "total_distance_km" in cost_df.columns:
            cost_df["total_distance_km"] = ensure_numeric(cost_df, "total_distance_km")
    else:
        cost_df = build_cost_evolution_from_travels(travels_df, period)
        if cost_df.empty:
            st.info("Sem dados suficientes para montar a evolucao de custos.")
            return
        cost_df = cost_df.rename(columns={"total_distance": "total_distance_km"})

    if "total_cost" not in cost_df.columns or cost_df["total_cost"].isna().all():
        st.info("Sem valores de custo para exibir no grafico.")
        return

    cost_df = cost_df.sort_values("period_label")
    fig_cost = px.line(
        cost_df,
        x="period_label",
        y="total_cost",
        markers=True,
        title="Evolucao de custos",
    )
    fig_cost.update_traces(mode="lines+markers")
    fig_cost.update_layout(hovermode="x unified")
    st.plotly_chart(fig_cost, use_container_width=True)

    if "total_distance_km" in cost_df.columns and cost_df["total_distance_km"].notna().any():
        fig_distance = px.bar(
            cost_df,
            x="period_label",
            y="total_distance_km",
            title="Distancia percorrida por periodo",
        )
        st.plotly_chart(fig_distance, use_container_width=True)


def render_top_travels(travels_df: pd.DataFrame) -> None:
    if travels_df.empty:
        st.info("Sem dados de viagens para listar.")
        return
    cost_col = first_valid_column(travels_df, COMMON_COST_COLUMNS)
    if not cost_col:
        st.info("Sem informacoes de custo por viagem para exibir ranking.")
        return

    work_df = travels_df.copy()
    work_df["cost_value"] = ensure_numeric(work_df, cost_col)
    work_df["distance_value"] = ensure_numeric(work_df, "full_distance")
    if work_df["cost_value"].isna().all():
        st.info("Sem informacoes de custo por viagem para exibir ranking.")
        return

    if "datetime" in work_df.columns:
        travel_datetime = pd.to_datetime(work_df["datetime"], errors="coerce")
    else:
        travel_datetime = pd.Series(pd.NaT, index=work_df.index)
    work_df = work_df.sort_values("cost_value", ascending=False).head(10)
    if not travel_datetime.empty:
        travel_datetime = travel_datetime.loc[work_df.index]
    else:
        travel_datetime = pd.Series(pd.NaT, index=work_df.index)

    unit_series = first_present_series(work_df, ("unit_name", "unit.name"))
    if unit_series is None and "unit_id" in work_df.columns:
        unit_series = work_df["unit_id"].astype(str)

    display_df = pd.DataFrame(index=work_df.index)
    display_df["Travel ID"] = work_df.get(
        "id", pd.Series(index=work_df.index, dtype=object)
    )
    display_df["Unidade"] = (
        unit_series
        if unit_series is not None
        else pd.Series(index=work_df.index, dtype=object)
    )
    display_df["Placa"] = work_df.get(
        "license_plate", pd.Series(index=work_df.index, dtype=object)
    )
    display_df["Data"] = travel_datetime.dt.strftime("%Y-%m-%d %H:%M").fillna("-")
    display_df["Distancia (km)"] = work_df["distance_value"].round(2)
    display_df["Custo (R$)"] = work_df["cost_value"].round(2)
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, hide_index=True)


def enrich_travels_with_bills(travels_df: pd.DataFrame, bills_df: pd.DataFrame) -> pd.DataFrame:
    if travels_df.empty or bills_df.empty:
        return travels_df
    if "id" not in travels_df.columns or "travel_id" not in bills_df.columns:
        return travels_df

    enriched = travels_df.copy()
    bills = bills_df.copy()

    enriched["id_str"] = enriched["id"].astype(str)
    bills["travel_id_str"] = bills["travel_id"].astype(str)

    cost_column = first_valid_column(bills, ("total_cost", "bill.total_cost", "cost"))
    if not cost_column and {"fix_cost", "variable_km"}.issubset(set(bills.columns)):
        distances = ensure_numeric(enriched, "full_distance").fillna(0)
        distance_map = dict(zip(enriched["id_str"], distances))
        fix_series = ensure_numeric(bills, "fix_cost").fillna(0)
        variable_series = ensure_numeric(bills, "variable_km").fillna(0)
        bills["total_cost_calc"] = fix_series + variable_series * bills["travel_id_str"].map(distance_map).fillna(0)
        cost_column = "total_cost_calc"

    if not cost_column:
        enriched.drop(columns=["id_str"], inplace=True)
        return enriched

    aggregated = (
        bills.groupby("travel_id_str")[cost_column].sum().reset_index().rename(columns={cost_column: "cost_from_bill"})
    )

    enriched = enriched.merge(aggregated, left_on="id_str", right_on="travel_id_str", how="left")
    if "bill.total_cost" in enriched.columns:
        enriched["bill.total_cost"] = enriched["bill.total_cost"].fillna(enriched["cost_from_bill"])
    else:
        enriched["bill.total_cost"] = enriched["cost_from_bill"]
    enriched.drop(columns=["id_str", "travel_id_str", "cost_from_bill"], inplace=True, errors="ignore")
    return enriched


def resolve_date_range(
    selection: Any,
    default_start: date,
    default_end: date,
) -> Tuple[date, date]:
    if isinstance(selection, (list, tuple)):
        if len(selection) >= 2:
            start, end = selection[0], selection[1]
        elif len(selection) == 1:
            start = end = selection[0]
        else:
            start, end = default_start, default_end
    elif isinstance(selection, date):
        start = end = selection
    else:
        start, end = default_start, default_end

    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()

    if start > end:
        start, end = end, start
    return start, end


def convert_date_to_iso(value: date, end_of_day: bool = False) -> str:
    target_time = time.max if end_of_day else time.min
    combined = datetime.combine(value, target_time)
    return combined.isoformat()


def main() -> None:
    st.title("Dashboard de Custos de Transporte")
    st.caption(
        "Painel interativo alimentado pela API Agro-Server para acompanhar gastos e desempenho das viagens."
    )

    with st.sidebar:
        st.header("Configurações")
        base_url = st.text_input("API base URL", value=DEFAULT_BASE_URL)
        token = st.text_input("Bearer token (opcional)", value=DEFAULT_TOKEN, type="password")

        use_mock = st.checkbox(
            "Usar dados simulados",
            value=False,
            help="Quando habilitado, o painel utiliza um conjunto de dados fictícios para demonstração.",
        )

        if st.button("Limpar cache de chamadas"):
            clear_fn = getattr(cached_get, "clear", None)
            if callable(clear_fn):
                clear_fn()
            st.success("Cache limpo com sucesso.")

        if use_mock:
            st.caption("Modo demonstração ativo: exibindo dados simulados.")

        period = st.selectbox(
            "Granularidade da evolução",
            PERIOD_CHOICES,
            index=PERIOD_CHOICES.index("month"),
            format_func=lambda key: PERIOD_LABELS.get(key, str(key)),
        )
        period_limit = st.slider("Quantidade de períodos", min_value=3, max_value=24, value=12)
        travel_limit = st.slider(
            "Máximo de viagens carregadas",
            min_value=50,
            max_value=500,
            value=200,
            step=50,
        )

        today = date.today()
        default_start = today - timedelta(days=90)
        date_selection = st.date_input(
            "Intervalo de datas",
            value=(default_start, today),
            max_value=today,
        )

        units_df = (
            get_mock_units_df()
            if use_mock
            else (
                build_dataframe(call_api(base_url, "units/", token=token))
                if base_url
                else pd.DataFrame()
            )
        )
        unit_options: Dict[str, Optional[str]] = {"Todas as unidades": None}

        if not units_df.empty:
            unit_name_col = first_valid_column(units_df, ("name", "unit.name"))
            unit_id_col = first_valid_column(units_df, ("id", "unit_id"))
            if unit_name_col or unit_id_col:
                sort_col = unit_name_col or unit_id_col
                if sort_col:
                    units_df_sorted = units_df.sort_values(by=sort_col)
                else:
                    units_df_sorted = units_df
            else:
                units_df_sorted = units_df

            for _, row in units_df_sorted.iterrows():
                unit_id = None
                if unit_id_col and unit_id_col in row.index and pd.notna(row[unit_id_col]):
                    unit_id = str(row[unit_id_col])
                if unit_id is None:
                    continue
                if unit_name_col and unit_name_col in row.index and pd.notna(row[unit_name_col]):
                    unit_label = str(row[unit_name_col])
                else:
                    unit_label = f"Unidade {unit_id}"
                unit_options[unit_label] = unit_id

        selected_unit_label = st.selectbox("Unidade", list(unit_options.keys()))
        selected_unit_id = unit_options[selected_unit_label]

    start_date, end_date = resolve_date_range(date_selection, default_start, today)

    summary_params: Dict[str, Any] = {
        "start_date": convert_date_to_iso(start_date),
        "end_date": convert_date_to_iso(end_date, end_of_day=True),
    }
    if selected_unit_id is not None:
        summary_params["unit_id"] = selected_unit_id

    travels_df = pd.DataFrame()
    bills_df = pd.DataFrame()
    summary_data: Optional[Dict[str, Any]] = None
    cost_payload: Optional[Dict[str, Any]] = None

    if use_mock:
        travels_df = get_mock_travels_df(selected_unit_id, start_date, end_date, travel_limit)
        summary_data = build_mock_summary(travels_df)
        cost_payload = build_mock_cost_payload(travels_df, period, period_limit)
        if not travels_df.empty and "id" in travels_df.columns:
            bills_df = get_mock_bills_df(travels_df["id"].tolist(), end_date)
    else:
        summary_payload = call_api(base_url, "dashboard/travel-summary/", summary_params, token)
        cost_params = {**summary_params, "period": period, "limit": period_limit}
        cost_payload = call_api(base_url, "dashboard/cost-evolution/", cost_params, token)

        travels_params = {**summary_params, "limit": travel_limit}
        travels_payload = call_api(base_url, "travels/", travels_params, token)
        travels_df = build_dataframe(travels_payload)
        summary_data = extract_first_dict(summary_payload)

    if not travels_df.empty and "datetime" in travels_df.columns:
        travels_df["datetime"] = pd.to_datetime(travels_df["datetime"], errors="coerce")
        travels_df = travels_df.sort_values("datetime", ascending=False)

    cost_column_present = first_valid_column(travels_df, COMMON_COST_COLUMNS) if not travels_df.empty else None

    if cost_column_present is None:
        if use_mock:
            if not bills_df.empty:
                travels_df = enrich_travels_with_bills(travels_df, bills_df)
                cost_column_present = first_valid_column(travels_df, COMMON_COST_COLUMNS)
        else:
            bills_payload = call_api(base_url, "bills/", summary_params, token)
            bills_df = build_dataframe(bills_payload)
            if not bills_df.empty:
                travels_df = enrich_travels_with_bills(travels_df, bills_df)
                cost_column_present = first_valid_column(travels_df, COMMON_COST_COLUMNS)
    elif not use_mock:
        bills_df = pd.DataFrame()

    metrics = compute_metrics(summary_data, travels_df, bills_df if not bills_df.empty else None)

    if use_mock:
        st.markdown("Fonte de dados: `mocked-data`")
    else:
        st.markdown(f"Fonte de dados: `{base_url}`")
    render_summary_cards(metrics)

    st.subheader("Evolução de custos")
    render_cost_chart(cost_payload, travels_df, period)

    st.subheader("Viagens com maior custo")
    render_top_travels(travels_df)

    st.subheader("Dados brutos")
    if travels_df.empty:
        st.info("Nenhuma viagem retornada para os filtros atuais.")
    else:
        display_df = travels_df.copy()
        if "datetime" in display_df.columns:
            display_df["datetime"] = display_df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        preferred_columns = [
            "id",
            "datetime",
            "license_plate",
            "asset_description",
            "full_distance",
            "bill.total_cost",
            "unit_name",
            "garage_name",
        ]
        visible_columns = [col for col in preferred_columns if col in display_df.columns]
        st.dataframe(
            display_df[visible_columns] if visible_columns else display_df,
            use_container_width=True,
            hide_index=True,
        )
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar dados em CSV",
            data=csv_bytes,
            file_name="travels.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
