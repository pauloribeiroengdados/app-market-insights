# Dashboard de Priorização — MBA Engenharia de Dados

## Sobre
Dashboard Streamlit para visualização e exportação das listas priorizadas de
reativação e prospecção de clientes, geradas pelo modelo XGBoost (Experimento E).

## Pré-requisitos
- Python 3.10+
- pip

## Instalação

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar o app
streamlit run app.py
```

## Uso com os parquets reais do projeto

1. Copie os arquivos abaixo para a mesma pasta do `app.py`:
   - `ml_score_reativacao_top5.parquet`
   - `ml_score_prospeccao_top5.parquet`

2. No app, desmarque **"Usar dados de demonstração"**

3. Informe os caminhos dos arquivos nos campos da sidebar

## Estrutura de colunas esperadas nos parquets

| Coluna | Tipo | Descrição |
|---|---|---|
| cnpj | str | CNPJ do estabelecimento |
| Razao_Social | str | Razão social |
| CNAE_Principal | str | Código CNAE principal |
| Porte | str | MEI / ME / EPP / Grande |
| uf_rfb | str | UF (MG, PR, RJ, RS, SP) |
| municipio_rfb | str | Município |
| capital_social | float | Capital social declarado (R$) |
| score_alto_valor | float | Score do modelo (0 a 1) |
| prioridade | str | Baixa / Media / Alta / Muito Alta |
| latitude | float | Latitude (opcional — para o mapa) |
| longitude | float | Longitude (opcional — para o mapa) |

## Funcionalidades

- Filtros por UF, Porte, CNAE, Prioridade e faixa de score
- KPIs: total de CNPJs, distribuição de prioridade, score médio
- Gráficos: distribuição por prioridade, por UF, histograma de score, por porte
- Mapa geográfico dos CNPJs de Alta e Muito Alta prioridade
- Tabela interativa com os CNPJs priorizados
- Export CSV da lista priorizada (Alta+Muito Alta ou todos os filtrados)

## Informações do modelo

- **Algoritmo:** XGBoost Classificador Binário
- **Formulação:** Alto Valor (Campeões + Fiéis + Potencial) vs Outros
- **Escopo:** Top 5 UFs — MG, PR, RJ, RS, SP
- **F1 Macro validação:** 0.7585
- **Versão:** 2 — dados corrigidos (base de inativos deduplificada)
