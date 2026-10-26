import pytest


def test_remove_a_coluna_customer_id(processor, df):
    resultado = processor.transform(df)

    assert "customerID" not in resultado.columns


def test_mapeia_yes_para_1(processor, df):
    resultado = processor.transform(df)

    assert resultado["Partner"].iloc[0] == 1


def test_mapeia_no_para_0(processor, df):
    resultado = processor.transform(df)

    assert resultado["Dependents"].iloc[0] == 0


def test_sem_telefone_vira_zero(processor, df):
    df["MultipleLines"] = "No phone service"

    resultado = processor.transform(df)

    assert resultado["MultipleLines"].iloc[0] == 0


def test_sem_internet_vira_zero(processor, df):
    df["OnlineSecurity"] = "No internet service"

    resultado = processor.transform(df)

    assert resultado["OnlineSecurity"].iloc[0] == 0


def test_cria_as_colunas_one_hot(processor, df):
    resultado = processor.transform(df)

    assert resultado["InternetService_DSL"].iloc[0] == 1
    assert "InternetService" not in resultado.columns


def test_nao_sobra_coluna_de_texto(processor, df):
    resultado = processor.transform(df)

    assert list(resultado.select_dtypes(include=["object", "str"]).columns) == []


def test_recusa_valor_desconhecido(processor, df):
    df["Partner"] = "Talvez"

    with pytest.raises(ValueError):
        processor.transform(df)
