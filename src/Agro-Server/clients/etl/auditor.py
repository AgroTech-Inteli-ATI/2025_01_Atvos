import pandas as pd
import numpy as np
import logging
from clients import bigquery_client

logger = logging.getLogger(__name__)

def audit_data(df):
    df['flag_divergencia'] = np.abs(df['km_variavel'] - df['km_esperado']) / df['km_esperado'] > 0.10
    df['score'] = 100 - (df['flag_divergencia'].astype(int) * 40)
    inconsistencias = df[df['flag_divergencia']]
    bigquery_client.load_dataframe(inconsistencias, 'your_dataset', 'inconsistencias')
    logger.info("Audit completed with %d inconsistencies", len(inconsistencias))