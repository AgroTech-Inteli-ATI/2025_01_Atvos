# 2025_01_Atvos
Plataforma de Auditoria de Logística — Agrotech Inteli para ATVOS

Projeto desenvolvido pela Agrotech Inteli em parceria com a ATVOS para automatizar a auditoria e o cálculo de custos de transporte de colaboradores. A solução ingere telemetria de veículos, identifica viagens de transporte de pessoal, calcula km variável segundo tarifas contratuais, consolida custos fixos e gera relatórios operacionais e financeiros (D-1 e mensais).

Visite a documentação completa em `docs/` (site gerado com Docusaurus) para detalhes de arquitetura, API e guias de uso.

Principais pontos
- **Stack:** Python (Django) no backend, Streamlit para dashboards, PostgreSQL (Supabase), S3 para armazenamento de Parquet, Docker/Docker Compose para ambiente.
- **Objetivo:** substituir registros manuais, aumentar a acurácia dos cálculos de km variável e fornecer transparência nos custos de transporte.
- **Deploy/CI:** integração com GitHub; site de documentação em Docusaurus (`docs/`).

Rápido guia de execução (desenvolvimento)

1. Documentação (site local)

	 - Instale dependências do site e rode localmente:

		 ```powershell
		 cd docs
		 yarn
		 yarn start
		 ```

2. Backend (Django) — execução local (opções)

	 - Recomendado: usar `docker-compose` para levantar serviços (Postgres, Supabase-like, etc.) se o `docker-compose.yaml` no `src/` estiver configurado.

	 - Execução direta (ambiente Python):

		 ```powershell
		 cd src/Agro-Server
		 python -m venv .venv
		 .\.venv\Scripts\Activate.ps1
		 pip install -r requirements.txt
		 cp .env.example .env  # ajustar variáveis (DATABASE_URL, SECRET_KEY, etc.)
		 python manage.py migrate
		 python manage.py runserver
		 ```

3. Frontend (Streamlit)

	 - O painel principal fica em `src/front/streamlit_app.py`.

		 ```powershell
		 cd src/front
		 python -m venv .venv
		 .\.venv\Scripts\Activate.ps1
		 pip install -r requirements.txt
		 streamlit run streamlit_app.py
		 ```

Estrutura do repositório (resumida)

- `src/Agro-Server/` — aplicativo Django (endpoints da API, ETL, management commands, migrations, testes).
- `src/clients/` — clientes e módulos ETL para ingestão e processamento de dados.
- `src/front/` — aplicação Streamlit para dashboards e uploads manuais.
- `docs/` — documentação do projeto (Docusaurus). Ver `docs/docs/intro.md` para visão geral e `docs/docs/Desenvolvimento-Inicial/03_Backend/backend.md` para documentação da API.
- `docker-compose.yaml` — orquestração local (quando aplicável).

Testes

- Existem testes para o backend em `src/Agro-Server/tests/` (ex.: `test_etl_service.py`). Rode-os com o runner apropriado do projeto (ex.: `pytest` ou `python manage.py test`).

Contribuição

- Abra uma issue descrevendo a proposta ou bug.
- Crie uma branch a partir de `develop` com nome descritivo.
- Faça PR para `develop` com descrição, checklist e testes quando aplicável.

Licença

- Consulte o arquivo `LICENSE` no repositório.

Contato

- Equipe Agrotech Inteli — para dúvidas sobre este repositório e entregáveis da ATVos.

---
> Documentação detalhada, endpoints e diagramas estão em `docs/`. Para instruções específicas de ambiente ou deploy, verifique as páginas `docs/docs/` correspondentes.
