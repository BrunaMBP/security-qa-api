import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash

from database import get_connection, init_db

app = Flask(__name__)

# Chave só para estudo. Em produção, vem de variável de ambiente.
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY",
    "chave-local-apenas-para-estudo-nao-usar-em-producao",
)

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 15

MAX_TENTATIVAS = 5
tentativas_falhas = {}


def token_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            return jsonify({"erro": "token de autenticação ausente"}), 401

        token = authorization.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"erro": "token de autenticação ausente"}), 401

        try:
            dados_token = jwt.decode(
                token,
                app.config["JWT_SECRET_KEY"],
                algorithms=[JWT_ALGORITHM],
            )
            username = dados_token.get("sub")
            if not isinstance(username, str) or not username:
                return jsonify({"erro": "token inválido"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "token inválido"}), 401

        request.username_autenticado = username
        return func(*args, **kwargs)

    return wrapper


@app.after_request
def adicionar_cabecalhos_de_seguranca(resposta):
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    resposta.headers["Cache-Control"] = "no-store"
    return resposta


@app.route("/login-inseguro", methods=["POST"])
def login_inseguro():
    # VULNERÁVEL DE PROPÓSITO: concatena entrada do usuário na query (SQL Injection).
    # Apenas para estudo, rodar somente localmente.
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    query = (
        "SELECT * FROM users_inseguro WHERE username = '" + username +
        "' AND password = '" + password + "'"
    )
    conn = get_connection()
    try:
        user = conn.execute(query).fetchone()
    except Exception:
        return jsonify({"erro": "erro na consulta"}), 500
    finally:
        conn.close()

    if user:
        return jsonify({"mensagem": "login ok"}), 200
    return jsonify({"erro": "credenciais inválidas"}), 401


@app.route("/login", methods=["POST"])
def login():
    # SEGURO: query parametrizada, hash de senha, limite de tentativas e JWT.
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"erro": "usuário e senha são obrigatórios"}), 400

    if tentativas_falhas.get(username, 0) >= MAX_TENTATIVAS:
        return jsonify({"erro": "muitas tentativas, tente mais tarde"}), 429

    conn = get_connection()
    user = conn.execute(
        "SELECT username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        tentativas_falhas.pop(username, None)

        agora = datetime.now(timezone.utc)
        payload = {
            "sub": user[0],
            "iat": agora,
            "exp": agora + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        }
        token = jwt.encode(
            payload,
            app.config["JWT_SECRET_KEY"],
            algorithm=JWT_ALGORITHM,
        )
        return jsonify({
            "mensagem": "login ok",
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": JWT_EXPIRATION_MINUTES * 60,
        }), 200

    tentativas_falhas[username] = tentativas_falhas.get(username, 0) + 1
    return jsonify({"erro": "credenciais inválidas"}), 401


@app.route("/perfil", methods=["GET"])
@token_obrigatorio
def perfil():
    return jsonify({
        "mensagem": "acesso autorizado",
        "username": request.username_autenticado,
    }), 200


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)