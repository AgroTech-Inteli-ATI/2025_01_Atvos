import pandas as pd
import numpy as np
import logging
from clients import bigquery_client

logger = logging.getLogger(__name__)

def run_audit(df):
    """
    Executa a auditoria nos dados transformados, identificando inconsistências.
    """
    if df.empty:
        logger.info("DataFrame de entrada está vazio. Nenhuma auditoria será aplicada.")
        return df
        
    # Calcula a variação percentual e sinaliza divergências acima de 10%
    df['flag_divergencia'] = np.abs(df['km_variavel'] - df['km_esperado']) / df['km_esperado'] > 0.10
    
    # Calcula um score de conformidade
    df['score'] = 100 - (df['flag_divergencia'].astype(int) * 40)
    
    # Loga o número de inconsistências encontradas
    inconsistencias_count = df['flag_divergencia'].sum()
    logger.info(f"Auditoria concluída. Encontradas {inconsistencias_count} inconsistências.")
    
    return df