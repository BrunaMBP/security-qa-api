import pytest

import database
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Usa um banco temporário, para não mexer no users.db real
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    app.config["TESTING"] = True
    return app.test_client()


def post(client, rota, username, password):
    return client.post(rota, json={"username": username, "password": password})


# ---------- Comportamento normal ----------

@pytest.mark.parametrize("rota", ["/login", "/login-inseguro"])
def test_login_valido(client, rota):
    assert post(client, rota, "admin", "admin123").status_code == 200


@pytest.mark.parametrize("rota", ["/login", "/login-inseguro"])
def test_senha_errada(client, rota):
    assert post(client, rota, "admin", "errada").status_code == 401


# ---------- SQL Injection ----------

PAYLOADS = [
    ("admin' --", "qualquer"),
    ("admin", "' OR '1'='1"),
    ("' OR '1'='1' --", "x"),
]


@pytest.mark.parametrize("username,password", PAYLOADS)
def test_sqli_funciona_na_rota_vulneravel(client, username, password):
    # Documenta a vulnerabilidade: o ataque DEVE funcionar aqui
    assert post(client, "/login-inseguro", username, password).status_code == 200


@pytest.mark.parametrize("username,password", PAYLOADS)
def test_sqli_barrado_na_rota_segura(client, username, password):
    assert post(client, "/login", username, password).status_code == 401


def test_aspas_simples_nao_gera_erro_500_na_rota_segura(client):
    assert post(client, "/login", "'", "'").status_code == 401


# ---------- Validação de entrada ----------

def test_campos_vazios_na_rota_segura(client):
    assert post(client, "/login", "", "").status_code == 400