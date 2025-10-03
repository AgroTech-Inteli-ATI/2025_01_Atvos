import pandas as pd
from datetime import timedelta, datetime
from .models import Vehicle, TelemetryRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_duration(duration_str: str) -> timedelta:
    """Convert duration string to timedelta"""
    try:
        hours, minutes = map(int, duration_str.split(':'))
        return timedelta(hours=hours, minutes=minutes)
    except:
        return timedelta()

def ingest_csv(filepath: str):
    """Carrega CSV de telemetria no formato Blocos de Veículo"""
    logger.info(f"Iniciando ingestão do arquivo: {filepath}")
    
    # Ler CSV ignorando cabeçalhos extras
    df = pd.read_csv(filepath, sep=",", encoding="latin-1", header=None, skip_blank_lines=False)
    logger.info(f"Arquivo carregado com {len(df)} linhas")

    # Debug: print first few rows to check data structure
    logger.debug(f"Primeiras linhas do arquivo:\n{df.head()}")

    current_vehicle_identifier = None
    records_created = 0

    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row[0]) or str(row[0]).strip() == "":
            continue

        # Detectar linha com Número de registro → identifier do veículo
        if isinstance(row[0], str) and "Número de registro" in row[0]:
            try:
                current_vehicle_identifier = str(row[2]).strip()
                logger.info(f"Processando veículo: {current_vehicle_identifier}")
                # Criar veículo se não existir
                vehicle, created = Vehicle.objects.get_or_create(identifier=current_vehicle_identifier)
                if created:
                    logger.info(f"Novo veículo criado: {current_vehicle_identifier}")
            except Exception as e:
                logger.error(f"Erro ao processar veículo na linha {idx}: {str(e)}")
            continue

        # Detectar linhas com telemetria: primeira coluna é data
        try:
            date_str = str(row[0]).strip()
            if "/" in date_str:  # data válida
                if not current_vehicle_identifier:
                    logger.warning(f"Linha {idx}: Registro encontrado sem veículo definido")
                    continue

                vehicle = Vehicle.objects.get(identifier=current_vehicle_identifier)

                # Safely get values with validation
                driver = str(row[1]) if not pd.isna(row[1]) else None
                date = datetime.strptime(date_str, "%d/%m/%Y")
                duration = parse_duration(str(row[4])) if not pd.isna(row[4]) else timedelta()
                distance = float(str(row[5]).replace(",", ".")) if not pd.isna(row[5]) else 0
                idle_time = parse_duration(str(row[12])) if len(row) > 12 and not pd.isna(row[12]) else timedelta()

                record = TelemetryRecord.objects.create(
                    vehicle=vehicle,
                    driver=driver,
                    date=date,
                    odometer=distance,
                    distance=distance,
                    duration=duration,
                    idle_time=idle_time
                )
                records_created += 1
                logger.info(f"Registro criado para {vehicle.identifier} em {date}")

        except Exception as e:
            logger.warning(f"Erro ao processar linha {idx}: {str(e)}")
            continue
    
    logger.info(f"Processamento finalizado. {records_created} registros criados.")