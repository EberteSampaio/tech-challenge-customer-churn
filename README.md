# Pipeline Preditivo de Churn

Modelo de classificação que estima a propensão de cancelamento de clientes de uma operadora de
telecomunicações, servido por uma API REST. Projeto da Fase 1 da Pós Tech em Machine Learning
Engineering (FIAP).

O repositório cobre o ciclo completo: análise exploratória, limpeza, comparação de modelos,
empacotamento do campeão e API de inferência.

## Contexto

Uma operadora perde clientes em ritmo acelerado e precisa identificar, antes do cancelamento, quem
está em risco — para que o time de retenção atue onde a oferta tem chance de reverter a saída.

A base tem 7.043 clientes e **26,5% de churn**, o que caracteriza um problema desbalanceado: um
modelo que simplesmente prevê "ninguém sai" acerta 73,5% das vezes e é inútil. Por isso a métrica
técnica principal é **PR-AUC** (`average_precision`), e não acurácia.

## Resultados

Modelo campeão: **Regressão Logística** com `class_weight="balanced"`, `C=1` e padronização.

| Métrica (conjunto de teste, 1.409 clientes) | Valor |
|---|---|
| PR-AUC | 0,631 |
| Recall (churn) | 0,706 |
| Precisão (churn) | 0,541 |
| Limiar de decisão | 0,5998 |

O limiar não é 0,5: foi escolhido maximizando F1 sobre a curva precision-recall em validação
cruzada. Na prática o modelo sinaliza 488 clientes para capturar 264 dos 374 que realmente saem.

Detalhes de desempenho, limitações e vieses estão no [Model Card](docs/model_card.md). A
formulação do problema, os stakeholders e a métrica de negócio estão no
[ML Canvas](docs/ml_canvas.md).

## Estrutura

```
.
├── data/
│   ├── raw/dataset.csv              base original (versionada)
│   └── processed/dataset_clean.csv  base tratada, entrada da modelagem
├── docs/
│   ├── ml_canvas.md                 problema, stakeholders e métricas de negócio
│   └── model_card.md                performance, limitações e vieses
├── models/churn_model.joblib        modelo campeão, limiar e contrato de colunas
├── notebooks/
│   ├── 01_eda.ipynb                 análise exploratória
│   ├── 02_data_cleaning.ipynb       limpeza e geração da base tratada
│   └── 03_modeling.ipynb            comparação de modelos e escolha do campeão
├── src/churn/
│   ├── main.py                      aplicação FastAPI
│   ├── cleaning/                    ColumnMapper e mapeamentos de domínio
│   ├── loader/                      leitura de CSV
│   ├── middleware/                  log estruturado das requisições
│   ├── model/                       carga do artefato e alinhamento de colunas
│   ├── processor/                   transformação de cliente cru em matriz do modelo
│   ├── router/                      endpoints /health e /predict
│   ├── schemas/                     contratos de entrada e saída (Pydantic)
│   └── service/                     orquestração da predição
└── tests/                           suíte pytest
```

A separação entre experimentação e produção é deliberada: os notebooks exploram, os módulos em
`src/` são o que a API executa. O `CustomerChurnProcessor` é compartilhado pelos dois, de modo que
o pré-processamento do treino e o da inferência não possam divergir.

## Requisitos

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) para gerenciar dependências

## Instalação

```bash
uv sync
```

Isso cria o `.venv` e instala as dependências de produção, de desenvolvimento e dos notebooks,
travadas pelo `uv.lock`.

## Executando a API

```bash
uv run uvicorn churn.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

### `GET /health/`

```bash
curl http://127.0.0.1:8000/health/
```

```json
{"status": "ok"}
```

### `POST /predict/`

```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H 'Content-Type: application/json' \
  -d '{
    "customerID": "0001-EXEMPLO",
    "gender": "Female",
    "SeniorCitizen": false,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 2,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 94.40,
    "TotalCharges": 188.80
  }'
```

```json
{"churn": true, "proba": 0.8941351149431376, "limiar": 0.5997756446847652}
```

A resposta devolve a probabilidade e o limiar usado, não apenas o rótulo — assim quem consome
entende por que uma propensão de 0,58 resulta em `false` e pode aplicar um corte próprio se o
custo da campanha de retenção mudar.

Campos categóricos aceitam apenas os valores presentes no treino. Qualquer outro valor devolve
**422** com a lista do que é aceito, em vez de uma predição silenciosamente errada:

```json
{"detail": [{"loc": ["body", "InternetService"],
             "msg": "Input should be 'DSL', 'Fiber optic' or 'No'"}]}
```

Por padrão o modelo é lido de `models/churn_model.joblib`. A variável de ambiente
`CHURN_MODEL_PATH` aponta para outro arquivo, útil em container.

## Testes

```bash
uv run pytest
```

São 18 testes divididos em três arquivos: o pré-processamento (`test_customer_churn_processor.py`),
a carga do modelo e o alinhamento das 26 colunas (`test_model_loader.py`) e os dois endpoints da
API (`test_api.py`), incluindo os casos de entrada inválida.

## Reproduzindo o pipeline

Os notebooks rodam em ordem e cada etapa consome a saída da anterior:

```bash
uv run jupyter lab
```

1. `01_eda.ipynb` — distribuição do alvo, ausentes, outliers e taxa de churn por variável.
2. `02_data_cleaning.ipynb` — gera `data/processed/dataset_clean.csv`.
3. `03_modeling.ipynb` — compara os modelos e grava `models/churn_model.joblib`.

Todas as etapas com aleatoriedade usam `random_state=42`. Os experimentos são registrados com
MLflow; para inspecioná-los:

```bash
uv run mlflow ui
```

## Decisões técnicas

**Por que PR-AUC e não acurácia.** Com 26,5% de positivos, a acurácia premia o modelo que ignora a
classe minoritária. O baseline sem balanceamento tem acurácia 0,81 contra 0,76 do campeão — e
mesmo assim é pior para o negócio, porque captura só 56% dos churners contra 71%.

**Por que Regressão Logística.** Ela empatou com Random Forest e superou Gradient Boosting e
MLPClassifier em PR-AUC na validação cruzada. Com desempenho equivalente, o modelo linear foi
escolhido por ser mais leve, mais rápido de servir e diretamente interpretável pelos coeficientes.

**Por que o limiar é ajustado.** O corte padrão de 0,5 do `predict()` não reflete o custo
assimétrico do erro: deixar de identificar quem vai sair custa mais caro do que oferecer desconto
a quem ficaria. O limiar de 0,5998 foi obtido maximizando F1 na curva precision-recall.

**Por que o contrato de colunas viaja com o modelo.** O artefato guarda `modelo`, `limiar` e
`colunas`. Um cliente isolado gera apenas as *dummies* das categorias que ele possui — 19 das 26
colunas. O `ChurnModel.align()` completa as ausentes com zero e reordena segundo a lista salva,
porque o `StandardScaler` registra `feature_names_in_` e recusa outra ordem.

## Limitações conhecidas

O modelo não identifica churn em dois grupos: clientes com contrato de dois anos e clientes sem
serviço de internet. Em ambos o recall no teste é zero. O [Model Card](docs/model_card.md) detalha
esses pontos cegos, as diferenças de desempenho entre subgrupos e os cuidados de uso.

No código, dois itens permanecem abertos:

- `/health` e `/predict` sem a barra final respondem **307** em vez de 200.
- `CustomerChurnProcessor.apply_raw_cleaning_data` altera o DataFrame recebido quando a coluna
  `customerID` já foi removida.

## Autor

Eberte Sampaio
