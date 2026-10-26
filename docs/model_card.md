# Model Card — Previsão de Churn

## Ficha técnica

| | |
|---|---|
| **Tarefa** | Classificação binária — propensão a cancelamento |
| **Algoritmo** | Regressão Logística (`class_weight="balanced"`, `C=1`) com `StandardScaler` |
| **Artefato** | `models/churn_model.joblib` — guarda o pipeline, o limiar e a ordem das colunas |
| **Entrada** | 26 variáveis numéricas derivadas de 19 atributos do cliente |
| **Saída** | Probabilidade em [0, 1] |
| **Limiar de decisão** | 0,5998 |
| **Ambiente** | Python 3.14.4, scikit-learn 1.9.1, pandas 3.0.6 |

## Uso pretendido

Priorizar a carteira de clientes de uma operadora de telecomunicações, indicando quem tem maior
propensão a cancelar para que o time de retenção direcione ofertas.

**Não deve ser usado** para decidir sozinho qualquer ação sobre o cliente, nem para negar serviço,
precificar risco ou priorizar atendimento. O modelo prevê saída, não risco de crédito — usá-lo
assim penalizaria os perfis descritos na seção de vieses. Os coeficientes indicam associação, não
causa.

## Dados

Telco Customer Churn (IBM), 7.043 clientes, **26,5% de churn**.

- Nenhum `customerID` duplicado; a coluna é descartada.
- 11 registros com `TotalCharges` em branco, todos com `tenure = 0` — clientes ainda não cobrados,
  preenchidos com 0.
- `"No internet service"` e `"No phone service"` são colapsados para `"No"`, já que a informação
  já está nas colunas `InternetService` e `PhoneService`.
- Partição: 5.634 treino / 1.409 teste, estratificada, `random_state=42`.

## Performance

Métrica principal: **PR-AUC**. Com 26,5% de positivos, a acurácia é enganosa — prever que ninguém
sai entrega 73,5% de acerto e valor zero.

| Classe | Precisão | Recall | F1 | Suporte |
|---|---|---|---|---|
| Não saiu | 0,88 | 0,78 | 0,83 | 1.035 |
| **Saiu** | **0,54** | **0,71** | **0,61** | **374** |

PR-AUC no teste: **0,631**. Acurácia: 0,76.

**Contra o baseline.** A regressão logística sem balanceamento tem acurácia maior (0,81 contra
0,76), mas recall de 0,56 contra 0,71: deixa passar 165 dos 374 clientes que saem, contra 110 do
modelo escolhido. A acurácia superior vem de acertar mais a classe que não interessa.

## Comparação de modelos

Validação cruzada estratificada de 5 folds sobre o treino:

| Modelo | Recall | Precisão | F1 | PR-AUC |
|---|---|---|---|---|
| **Regressão Logística (balanced)** | **0,801** | **0,518** | **0,629** | **0,660** |
| Regressão Logística | 0,544 | 0,653 | 0,593 | 0,662 |
| Regressão Logística + SMOTE | 0,792 | 0,525 | 0,631 | 0,659 |
| Random Forest | 0,812 | 0,508 | 0,625 | 0,656 |
| Gradient Boosting | 0,552 | 0,587 | 0,569 | 0,612 |
| MLPClassifier | 0,653 | 0,538 | 0,590 | 0,586 |

Os quatro primeiros empatam dentro da margem de ruído (0,656 a 0,662). O desempate foi por
simplicidade: o modelo linear é mais leve de servir e tem coeficientes auditáveis.

## Desempenho por subgrupo

Medido no teste, com o modelo treinado apenas na partição de treino.

| Subgrupo | n | Churn real | Recall | Precisão |
|---|---|---|---|---|
| Geral | 1.409 | 26,5% | 0,706 | 0,541 |
| Feminino | 687 | 28,1% | 0,699 | 0,565 |
| Masculino | 722 | 25,1% | 0,713 | 0,518 |
| Idoso | 222 | 44,1% | 0,827 | 0,591 |
| Não idoso | 1.187 | 23,3% | 0,663 | 0,521 |
| Contrato mensal | 773 | 42,6% | 0,790 | 0,545 |
| Contrato de dois anos | 336 | 2,7% | **0,000** | — |
| Fibra óptica | 613 | 41,1% | 0,853 | 0,557 |
| Sem internet | 312 | 8,0% | **0,000** | — |

## Limitações

**Dois pontos cegos completos.** O modelo não identificou nenhum dos 9 churners com contrato de
dois anos, nem nenhum dos 25 sem serviço de internet — não sinalizou um único cliente desses
grupos. Para eles, o time de retenção precisa de outro critério.

**Coeficientes não são interpretáveis isoladamente.** `MonthlyCharges` tem coeficiente negativo
(−0,96) e `TotalCharges` positivo (+0,49), o que contraria a intuição. A causa é
multicolinearidade: `TotalCharges ≈ tenure × MonthlyCharges`. Remover `TotalCharges` quase não
altera o desempenho (PR-AUC de 0,660 para 0,658), o que confirma a redundância.

**Modelo estático.** Não há detecção de *drift* nem retreino automático; o desempenho vai degradar
sem aviso.

**Fotografia, não série temporal.** A base é um retrato único. Um cliente cujo consumo vem caindo
há três meses é indistinguível de um estável com o mesmo valor atual.

**Artefato retreinado em 100% dos dados.** As métricas acima vêm da versão treinada só no treino —
são a melhor estimativa disponível, mas não foram medidas no objeto exato que está servindo.

**Teto do problema.** O empate entre quatro famílias de modelos sugere que o limite está nas
variáveis disponíveis, não no algoritmo. Ganhos relevantes exigem dados novos — histórico de
chamados, reclamações, uso mensal.

## Vieses

**Gênero: sem disparidade relevante.** As taxas reais são próximas (26,9% feminino, 26,2%
masculino) e o recall é equilibrado (0,699 contra 0,713). O coeficiente de `gender` é −0,016, o
menor em magnitude de todo o modelo.

**Faixa etária: recall de 0,827 para idosos contra 0,663 para os demais.** No uso pretendido isso
não é prejudicial — ser sinalizado resulta em receber uma oferta, ou seja, um benefício. O
problema se inverteria se o modelo passasse a restringir acesso ou precificar risco, e é por isso
que esses usos estão vedados acima.

**Variáveis sensíveis no modelo.** `gender`, `SeniorCitizen`, `Partner` e `Dependents` são
atributos pessoais usados como preditores, todos com coeficientes pequenos. Removê-los teria
impacto marginal e eliminaria o risco de a operadora decidir sobre clientes com base em estado
civil ou idade.

**Desigualdade herdada dos dados.** Clientes sem parceiro (33,0% contra 19,7%) e sem dependentes
(31,3% contra 15,5%) cancelam mais, e o modelo reproduz esse padrão.

**Privacidade.** O middleware registra o corpo completo da requisição, incluindo `customerID`, em
texto puro. Antes de uso real isso precisa ser mascarado, sob risco de violar a LGPD.

## Recomendações

1. Tratar a saída como priorização, com revisão humana antes de qualquer ação.
2. Usar `proba` em vez do rótulo quando a área quiser seu próprio corte.
3. Adotar critério alternativo para contratos de dois anos e clientes sem internet.
4. Recalibrar o limiar se o custo da campanha mudar — o 0,5998 otimiza F1, não lucro.
5. Monitorar a taxa de churn observada e retreinar quando divergir dos 26,5% documentados.
