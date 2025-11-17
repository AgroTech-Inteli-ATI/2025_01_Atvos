import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def transform_data(df):
    df = df.drop_duplicates(subset=['id'])
    df['odometro_inicio'] = pd.to_numeric(df['odometro_inicio'], errors='coerce')
    df['odometro_fim'] = pd.to_numeric(df['odometro_fim'], errors='coerce')
    df['km_variavel'] = df['odometro_fim'] - df['odometro_inicio']
    df['km_variavel'] = df['km_variavel'].where(df['km_variavel'] >= 0, np.nan)
    df['custos_consolidados'] = df['custos_fixos'] + df['custos_variaveis']
    logger.info("Transformed data with %d records", len(df))
    return df