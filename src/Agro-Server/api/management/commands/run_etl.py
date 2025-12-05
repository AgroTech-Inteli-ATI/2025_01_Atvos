import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from clients.etl.extractor import extract_data
from clients.etl.transformer import transform_data
from clients.etl.loader import upload_to_gcs_and_load_bq
from clients.etl.auditor import run_audit

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Executa o pipeline ETL: extração do Django, transformação, carga no BigQuery e auditoria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a execução mesmo se já rodou hoje',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(f'Iniciando ETL em {start_time}')

        try:
            # 1. Extração dos dados
            self.stdout.write('1. Extraindo dados do Django...')
            raw_data = extract_data()
            
            # 2. Transformação
            self.stdout.write('2. Transformando dados...')
            transformed_data = transform_data(raw_data)
            
            # 3. Carga no GCS e BigQuery
            self.stdout.write('3. Carregando dados no GCS e BigQuery...')
            gcs_uri = upload_to_gcs_and_load_bq(
                transformed_data,
                prefix=f'etl/viagens_{start_time.strftime("%Y%m%d")}',
                table_name='viagens_cleaned'
            )
            
            # 4. Auditoria
            self.stdout.write('4. Executando auditoria...')
            audit_results = run_audit(transformed_data)
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            # Verifica se o DataFrame de auditoria não está vazio antes de contar as inconsistências
            if not audit_results.empty:
                inconsistencias_count = len(audit_results[audit_results["flag_divergencia"]])
            else:
                inconsistencias_count = 0

            self.stdout.write(self.style.SUCCESS(
                f'''
                ETL concluído com sucesso!
                - Registros processados: {len(transformed_data)}
                - Inconsistências encontradas: {inconsistencias_count}
                - Arquivo GCS: {gcs_uri}
                - Tempo total: {duration.total_seconds():.2f}s
                '''
            ))

        except Exception as e:
            logger.exception('Erro durante execução do ETL')
            self.stdout.write(
                self.style.ERROR(f'Erro durante execução do ETL: {str(e)}')
            )
            raise