import pytest

from churn.model import load_churn_model


def test_carrega_o_modelo_salvo(model):
    assert model.pipeline is not None
    assert len(model.columns) == 26


def test_o_limiar_nao_e_o_padrao_de_meio(model):
    assert model.limiar != 0.5


def test_avisa_quando_o_arquivo_nao_existe(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_churn_model(tmp_path / "nao_existe.joblib")


def test_align_completa_as_colunas_que_faltam(model, processor, df):
    """Um cliente só gera as dummies das categorias dele; o resto vai a zero."""
    transformado = processor.transform(df)

    alinhado = model.align(transformado)

    assert list(alinhado.columns) == model.columns
    assert alinhado["Contract_Two year"].iloc[0] == 0


def test_a_probabilidade_fica_entre_zero_e_um(model, processor, df):
    proba = model.proba(processor.transform(df))

    assert 0.0 <= proba <= 1.0
