def test_register_and_login(client):
    # Registro
    r = client.post("/api/v1/auth/register", json={
        "name": "João Silva",
        "email": "joao@example.com",
        "password": "senha_segura_123",
    })
    assert r.status_code == 201
    assert r.json()["email"] == "joao@example.com"

    # Login
    r = client.post("/api/v1/auth/login", json={
        "email": "joao@example.com",
        "password": "senha_segura_123",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_email(client):
    payload = {"name": "A", "email": "a@b.com", "password": "123456"}
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409