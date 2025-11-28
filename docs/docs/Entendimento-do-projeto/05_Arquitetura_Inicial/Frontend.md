---
sidebar\_position: 2
slug: /sprint-1/arquitetura/frontend
description: "Especificação da arquitetura do frontend"
---

# Arquitetura do Frontend

&ensp; Este documento detalha a arquitetura do frontend da aplicação, com foco na escolha tecnológica, estrutura do projeto e componentes de interface. A seção apresenta as justificativas para a adoção do Streamlit, as bibliotecas auxiliares utilizadas, a organização de pastas, o gerenciamento de estado e aspectos de design, responsividade e acessibilidade, evidenciando como a interface foi planejada para ser eficiente, intuitiva e voltada à visualização de dados.

## Tecnologia Escolhida

Embora React seja uma biblioteca poderosa para construção de interfaces web complexas e altamente interativas, **Streamlit** foi escolhido por sua simplicidade e foco em dashboards e aplicações de dados. Streamlit permite a construção rápida de interfaces web interativas diretamente em Python, sem necessidade de configuração complexa de front-end ou integração com APIs REST.

### Justificativa da Escolha

* **Agilidade:** Permite criar dashboards e relatórios de forma rápida.
* **Integração com Python:** Facilita o consumo de dados processados no backend, principalmente cálculos de telemetria e auditoria.
* **Manutenção Simplificada:** Menor complexidade de arquitetura comparado a um front-end em React.
* **Foco em Dados:** Ideal para aplicações que priorizam visualização e análise de dados operacionais e financeiros.

### Bibliotecas Auxiliares

* **Pandas / Numpy:** Manipulação de dados para exibição em dashboards.
* **Plotly / Matplotlib / Seaborn:** Visualização gráfica interativa e estatística.
* **Streamlit-AgGrid:** Tabelas interativas com funcionalidades avançadas.
* **SessionState (ou st.session\_state):** Controle de estado entre interações.


## Estrutura do Projeto
&ensp; A estrutura do projeto define como os arquivos, pastas e módulos estão organizados. Ela facilita a colaboração, a manutenção do código e a escalabilidade do sistema.

### Organização de Pastas

```
/frontend
├─ /pages            # Páginas do Streamlit (cada arquivo = uma página)
├─ /components       # Componentes reutilizáveis (cards, gráficos, filtros)
├─ /data             # Dados estáticos ou exemplos para desenvolvimento
├─ /utils            # Funções utilitárias (cálculos, formatação, helpers)
└─ main.py           # Arquivo principal que inicializa o app
```

### Componentes Reutilizáveis

* **Gráficos:** Funções para plotar gráficos de viagens, custos e divergências.
* **Filtros:** Seletores de datas, veículos, transportadoras e turnos.
* **Cards e KPIs:** Visualização rápida de métricas-chave (km variável, custo total, divergências).
* **Tabelas Interativas:** Exibição de boletins e auditorias com paginação e ordenação.

### Gerenciamento de Estado

* **st.session\_state:** Controla dados persistentes entre interações, como filtros aplicados e dados carregados do backend.
* **Callbacks e funções:** Cada interação do usuário (seleção de filtros, upload de arquivos) dispara funções que atualizam `st.session_state` e re-renderizam componentes.


## Interface do Usuário
&ensp; A interface do usuário (UI) é a camada visual e interativa de um sistema. Ela permite que o usuário se comunique com o software de forma intuitiva e eficiente.

### Design System

* Paleta de cores consistente com a identidade corporativa.
* Tipografia clara e legível para dashboards operacionais.
* Componentes uniformes para gráficos, tabelas e cards.

### Responsividade

* Layouts adaptáveis para diferentes resoluções de tela.
* Componentes reorganizáveis verticalmente (Streamlit é naturalmente responsivo em telas menores).

### Acessibilidade

* Textos alternativos para gráficos e imagens.
* Contraste adequado de cores.
* Navegação por teclado suportada.

## Conclusões
&ensp; A arquitetura do frontend, baseada em Streamlit, permite desenvolvimento ágil, manutenção simplificada e integração direta com o backend em Python. A estrutura modular, o gerenciamento de estado eficiente e o design consistente garantem que a aplicação seja responsiva, acessível e capaz de fornecer dashboards claros e interativos para análise de dados operacionais e financeiros.