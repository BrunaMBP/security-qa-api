import pytest
from app import app
import database


@pytest.fixture
def client():
    # Configura o banco e a app para modo de teste
    database.init_db()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_bloqueio_rota_protegida_sem_token(client):
    """Garante que a rota /perfil rejeita acessos sem token JWT"""
    response = client.get("/perfil")
    assert response.status_code == 401
    assert response.json["erro"] == "token de autenticação ausente"


def test_fluxo_autenticacao_jwt_sucesso(client):
    """Testa o fluxo completo: login, captura do token e acesso ao /perfil"""
    # 1. Login com credenciais válidas
    payload = {"username": "admin", "password": "admin123"}
    response_login = client.post("/login", json=payload)

    assert response_login.status_code == 200
    assert "access_token" in response_login.json

    token = response_login.json["access_token"]

    # 2. Requisição para a rota protegida com o token JWT
    headers = {"Authorization": f"Bearer {token}"}
    response_perfil = client.get("/perfil", headers=headers)

    assert response_perfil.status_code == 200
    assert response_perfil.json["username"] == "admin"