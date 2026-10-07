from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash

from database import get_connection, init_db

app = Flask(__name__)

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
    # SEGURO: query parametrizada + senha verificada por hash.
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"erro": "usuário e senha são obrigatórios"}), 400

    conn = get_connection()
    user = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        return jsonify({"mensagem": "login ok"}), 200
    return jsonify({"erro": "credenciais inválidas"}), 401


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)