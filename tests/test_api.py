def test_health_responde_ok(client):
    resposta = client.get("/health/")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_predict_responde_com_sucesso(client, payload):
    resposta = client.post("/predict/", json=payload)

    assert resposta.status_code == 200


def test_predict_devolve_a_probabilidade(client, payload):
    corpo = client.post("/predict/", json=payload).json()

    assert 0.0 <= corpo["proba"] <= 1.0
    assert corpo["churn"] == (corpo["proba"] >= corpo["limiar"])


def test_recusa_categoria_que_nao_existe(client, payload):
    payload["Contract"] = "Mensal"

    resposta = client.post("/predict/", json=payload)

    assert resposta.status_code == 422


def test_recusa_payload_incompleto(client, payload):
    del payload["Contract"]

    resposta = client.post("/predict/", json=payload)

    assert resposta.status_code == 422
