from datetime import date, datetime, timedelta, timezone


def _auth_headers(client, email="maria@example.com"):
    client.post("/api/v1/auth/register", json={
        "name": "Maria", "email": email, "password": "senha_segura_123",
    })
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "senha_segura_123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_users_me(client):
    headers = _auth_headers(client)
    r = client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "maria@example.com"
    assert "hashed_password" not in r.json()


def test_rotas_protegidas_sem_token(client):
    for path in ("/api/v1/users/me", "/api/v1/clients/", "/api/v1/dashboard/summary"):
        assert client.get(path).status_code in (401, 403), path


def test_fluxo_cliente_cobranca_pagamento_dashboard(client):
    headers = _auth_headers(client)

    # Cliente
    r = client.post("/api/v1/clients/", headers=headers, json={
        "name": "Padaria do Zé", "phone": "(31) 99999-0000", "email": "ze@padaria.com",
    })
    assert r.status_code == 201, r.text
    cliente = r.json()
    assert cliente["phone"] == "31999990000"

    r = client.get("/api/v1/clients/", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["name"] == "Padaria do Zé"

    r = client.put(f"/api/v1/clients/{cliente['id']}", headers=headers, json={"notes": "paga no dia 10"})
    assert r.status_code == 200 and r.json()["notes"] == "paga no dia 10"

    # Cobrança
    r = client.post("/api/v1/charges/", headers=headers, json={
        "client_id": cliente["id"],
        "amount": "150.00",
        "description": "Mensalidade",
        "due_date": (date.today() + timedelta(days=5)).isoformat(),
        "send_at": datetime.now(timezone.utc).isoformat(),
    })
    assert r.status_code == 201, r.text
    cobranca = r.json()

    r = client.get("/api/v1/charges/", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["total"] == 1

    # Pagamento parcial e depois o restante
    url_pag = f"/api/v1/charges/{cobranca['id']}/payments/"
    r = client.post(url_pag, headers=headers, json={
        "amount_paid": "50.00", "payment_date": date.today().isoformat(), "method": "pix",
    })
    assert r.status_code == 201, r.text
    assert client.get(f"/api/v1/charges/{cobranca['id']}", headers=headers).json()["status"] == "partially_paid"

    r = client.get("/api/v1/dashboard/summary", headers=headers)
    assert r.status_code == 200, r.text
    resumo = r.json()
    assert resumo["total_partially_paid"] == 1
    assert float(resumo["amount_to_receive"]) == 100.0
    assert float(resumo["amount_received"]) == 50.0

    client.post(url_pag, headers=headers, json={
        "amount_paid": "100.00", "payment_date": date.today().isoformat(), "method": "pix",
    })
    detalhe = client.get(f"/api/v1/charges/{cobranca['id']}", headers=headers).json()
    assert detalhe["status"] == "paid"
    assert len(detalhe["payments"]) == 2

    resumo = client.get("/api/v1/dashboard/summary", headers=headers).json()
    assert resumo["total_paid"] == 1
    assert float(resumo["amount_to_receive"]) == 0.0
    assert float(resumo["amount_received"]) == 150.0


def test_cliente_de_outro_usuario_nao_aparece(client):
    h1 = _auth_headers(client, "a@example.com")
    h2 = _auth_headers(client, "b@example.com")
    r = client.post("/api/v1/clients/", headers=h1, json={"name": "X", "phone": "31999990000"})
    cid = r.json()["id"]
    assert client.get(f"/api/v1/clients/{cid}", headers=h2).status_code == 404
    assert client.get("/api/v1/clients/", headers=h2).json()["total"] == 0
