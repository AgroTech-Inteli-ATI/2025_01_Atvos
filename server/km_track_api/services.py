import pandas as pd
from datetime import timedelta, datetime
from .models import Vehicle, TelemetryRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_csv(filepath: str):
    """Carrega CSV de telemetria"""
    logger.info(f"Iniciando ingestão do arquivo: {filepath}")
    
    df = pd.read_csv(filepath, sep=",", encoding="latin-1")
    logger.info(f"Arquivo carregado com {len(df)} linhas")

    records_created = 0

    for idx, row in df.iterrows():
        try:
            # Safely extract plate number
            if pd.isna(row[1]):
                logger.warning(f"Linha {idx}: Placa não encontrada")
                continue
                
            parts = str(row[1]).split()
            if len(parts) < 2:
                logger.warning(f"Linha {idx}: Formato de placa inválido")
                continue
                
            placa = parts[-2]  # Get the second to last part
            
            # Create or get vehicle
            vehicle, created = Vehicle.objects.get_or_create(identifier=placa)
            if created:
                logger.info(f"Novo veículo criado: {placa}")

            # Create telemetry record
            record = TelemetryRecord.objects.create(
                vehicle=vehicle,
                date=row['Data'],
                driver=row['Motorista'],
                total_km_traveled=float(str(row['Distância']).replace(',', '.')),
                duration=timedelta(hours=int(row['Tempo'].split(':')[0]), 
                                 minutes=int(row['Tempo'].split(':')[1])),
                odometer=float(str(row['Hodômetro']).replace(',', '.'))
            )
            records_created += 1
            logger.info(f"Registro criado para {placa}")

        except Exception as e:
            logger.error(f"Erro ao processar linha {idx}: {str(e)}")
            continue

    logger.info(f"Processamento finalizado. {records_created} registros criados.")