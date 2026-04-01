# App Market Insights — MBA Engenharia de Dados

## Sobre
App para visualização e exportação das listas priorizadas de
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
- **Versão:** 2 — dados corrigidos (base de inativos dedupliplicada)
