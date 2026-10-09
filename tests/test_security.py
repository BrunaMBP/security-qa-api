from datetime import datetime, timedelta, timezone

import jwt
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


def test_senha_nao_fica_em_texto_puro(client):
    conn = database.get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", ("admin",)
    ).fetchone()
    conn.close()
    assert row[0] != "admin123"
    assert row[0].startswith(("scrypt:", "pbkdf2:"))


# ---------- Cabeçalhos de segurança ----------

CABECALHOS_ESPERADOS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


@pytest.mark.parametrize("rota", ["/login", "/login-inseguro"])
def test_cabecalhos_de_seguranca_presentes(client, rota):
    resposta = post(client, rota, "admin", "admin123")
    for nome, valor in CABECALHOS_ESPERADOS.items():
        assert resposta.headers.get(nome) == valor
    assert "default-src 'none'" in resposta.headers.get("Content-Security-Policy", "")


def test_cabecalhos_presentes_tambem_em_resposta_de_erro(client):
    resposta = post(client, "/login", "admin", "errada")
    assert resposta.status_code == 401
    assert resposta.headers.get("X-Content-Type-Options") == "nosniff"    

# ---------- Autenticação por token (JWT) ----------

def obter_token(client):
    return post(client, "/login", "admin", "admin123").get_json()["access_token"]


def test_perfil_sem_token_retorna_401(client):
    assert client.get("/perfil").status_code == 401


def test_perfil_com_token_valido(client):
    token = obter_token(client)
    resposta = client.get("/perfil", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    assert resposta.get_json()["username"] == "admin"


def test_perfil_com_token_adulterado(client):
    cabecalho, payload, _ = obter_token(client).split(".")
    falso = f"{cabecalho}.{payload}.assinaturafalsa"
    resposta = client.get("/perfil", headers={"Authorization": f"Bearer {falso}"})
    assert resposta.status_code == 401


def test_perfil_com_token_expirado(client):
    agora = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "admin", "iat": agora - timedelta(hours=2), "exp": agora - timedelta(hours=1)},
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    resposta = client.get("/perfil", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_perfil_com_token_assinado_por_outra_chave(client):
    agora = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "admin", "exp": agora + timedelta(minutes=5)},
        "outra-chave-diferente-com-mais-de-trinta-e-dois-bytes",
        algorithm="HS256",
    )
    resposta = client.get("/perfil", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_perfil_rejeita_token_com_algoritmo_none(client):
    agora = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "admin", "exp": agora + timedelta(minutes=5)},
        key=None,
        algorithm="none",
    )
    resposta = client.get("/perfil", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401