# ML Canvas — Previsão de Churn

Formulação do problema segundo o Machine Learning Canvas. Performance, limitações e vieses estão
no [Model Card](model_card.md).

## Proposta de valor

Uma operadora de telecomunicações perde 26,5% da base e só percebe o cancelamento depois que ele
acontece. O modelo estima a propensão de cada cliente a cancelar, para que o time de retenção —
que tem orçamento e capacidade de contato limitados — saiba quem abordar primeiro.

## Stakeholders

| Papel | Interesse |
|---|---|
| Diretoria | Reduzir churn e proteger a receita recorrente |
| Time de retenção | Saber quem abordar primeiro — usuário final da priorização |
| CRM / Engenharia | Integrar a predição ao fluxo de campanhas via API |
| Ciência de dados | Manter o modelo calibrado e monitorado |
| Jurídico | Conformidade com a LGPD no uso de dados pessoais |
| Cliente final | Não ser penalizado por uma classificação automática |

O cliente final não tem voz no processo. Por isso o Model Card veda usar o modelo para precificar
risco ou restringir acesso: no uso previsto, ser sinalizado significa receber um benefício.

## Decisões

Incluir ou não um cliente na próxima campanha de retenção. Quem decide é o time de retenção — a
saída é insumo de priorização, nunca ação automática.

Clientes acima de **0,5998** entram na lista. O limiar não é o 0,5 padrão porque deixar de
identificar quem vai sair custa mais do que oferecer desconto a quem ficaria.

Em contratos de dois anos e clientes sem internet o modelo não dá sinal útil; o time precisa de
outro critério.

## Tarefa de ML

Classificação binária supervisionada. Entrada: 19 atributos cadastrais e de contrato. Saída:
probabilidade de cancelamento. Desbalanceamento de 26,5% tratado com `class_weight="balanced"`.

## Fontes de dados

Telco Customer Churn (IBM), 7.043 clientes, versionado em `data/raw/dataset.csv`. Em produção o
equivalente seria o sistema de faturamento, o cadastro de clientes e o catálogo de contratos.

Faltam dados que fariam diferença: histórico de chamados, reclamações, interrupções de serviço e
uso mensal.

## Coleta de dados

Neste projeto, um snapshot único e estático — não há coleta contínua. Em produção seria necessária
extração mensal, com o rótulo observado após a janela de cancelamento, permitindo acompanhar a
trajetória de cada cliente.

## Features

26 colunas numéricas produzidas por `CustomerChurnProcessor`:

- Binárias mapeadas para 0/1: `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`,
  `gender`, `SeniorCitizen`.
- `MultipleLines` e as seis dependentes de internet, com `"No phone service"` e
  `"No internet service"` colapsados para `"No"`.
- Numéricas diretas: `tenure`, `MonthlyCharges`, `TotalCharges`.
- One-hot: `PaymentMethod`, `InternetService`, `Contract`.

Descartada: `customerID`. Mais influentes: `tenure` (−1,15), `InternetService_Fiber optic` (+0,69),
`Contract_Month-to-month` (+0,32).

## Construção dos modelos

Treino offline, executado uma vez. Seis candidatos avaliados em validação cruzada estratificada de
5 folds: Regressão Logística (pura, balanceada e com SMOTE), Random Forest, Gradient Boosting e
MLPClassifier.

Escolhida a Regressão Logística balanceada. `random_state=42` em todas as etapas, experimentos
rastreados com MLflow. O mesmo código de pré-processamento serve o treino e a API, de modo que não
possam divergir.

## Geração das predições

Sob demanda, um cliente por requisição, via `POST /predict`. O modelo é carregado uma vez por
processo e reaproveitado. Latência mediana de 37 ms (p95 de 63 ms).

Categorias são validadas contra os valores vistos no treino: um valor desconhecido devolve **422**
em vez de uma predição silenciosamente errada. A resposta traz a probabilidade, o rótulo e o
limiar aplicado.

## Avaliação offline

PR-AUC como métrica principal, porque com 26,5% de positivos a acurácia premia quem ignora a
classe minoritária. No teste: PR-AUC 0,631, recall 0,706, precisão 0,541.

## Métricas de negócio

A campanha se paga enquanto:

```
custo_do_contato  <  precisão × valor_do_cliente_retido × taxa_de_sucesso_da_oferta
```

Com precisão de 0,541, o ponto de equilíbrio é **54%**: abordar um cliente precisa custar menos
que 54% do valor esperado de uma retenção.

No conjunto de teste, 488 clientes seriam sinalizados para capturar 264 dos 374 que realmente
saem, com 224 contatos desperdiçados. Os valores monetários dependem do ticket médio e da taxa de
conversão, a definir pela área de negócio — e se essa relação mudar, o limiar precisa ser
recalibrado.

## Monitoramento

A acompanhar: distribuição das entradas contra a do treino, taxa de churn observada, precisão e
recall reais das campanhas, e volume de respostas 422.

Hoje não existe detecção automática de *drift* nem retreino programado — a revisão depende de
acompanhamento manual, sugerida a cada trimestre.
