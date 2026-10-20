import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


def test_bloqueio_rota_protegida_sem_token():
    """Garante que a rota /perfil rejeita acessos sem token JWT"""
    response = requests.get(f"{BASE_URL}/perfil")
    assert response.status_code == 401
    assert response.json()["erro"] == "token de autenticação ausente"


def test_fluxo_autenticacao_jwt_sucesso():
    """Testa o fluxo completo: login, captura do token e acesso ao /perfil"""
    # 1. Login com credenciais válidas
    payload = {"username": "admin", "password": "admin123"}
    response_login = requests.post(f"{BASE_URL}/login", json=payload)

    assert response_login.status_code == 200
    assert "access_token" in response_login.json()

    token = response_login.json()["access_token"]

    # 2. Requisição para a rota protegida com o token JWT
    headers = {"Authorization": f"Bearer {token}"}
    response_perfil = requests.get(f"{BASE_URL}/perfil", headers=headers)

    assert response_perfil.status_code == 200
    assert response_perfil.json()["username"] == "admin"
