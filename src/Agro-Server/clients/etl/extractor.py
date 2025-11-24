import logging
import pandas as pd
from django.apps import apps

logger = logging.getLogger(__name__)

def extract_data(model_app='api', model_name='Viagem'):
    Viagem = apps.get_model(model_app, model_name)
    qs = Viagem.objects.all().iterator()
    records = []
    for v in qs:
        records.append({
            'id': v.id,
            'veiculo_id': v.veiculo_id,
            'odometro_inicio': v.odometro_inicio,
            'odometro_fim': v.odometro_fim,
            'ts_inicio': v.ts_inicio,
            'ts_fim': v.ts_fim,
            'gps_path': v.gps_path,
            'custos_fixos': v.custos_fixos,
            'custos_variaveis': v.custos_variaveis,
        })
    df = pd.DataFrame.from_records(records)
    logger.info("Extracted %d records", len(df))
    return df