# Security QA API (em andamento)

![Testes](https://github.com/BrunaMBP/security-qa-api/actions/workflows/tests.yml/badge.svg)

Projeto de estudo de **Security QA**: uma API Flask com duas versões do mesmo login, uma **propositalmente vulnerável** a SQL Injection e outra segura, com testes automatizados que provam a diferença entre as duas.

> **Aviso:** a rota `/login-inseguro` é vulnerável de propósito, para fins educacionais.

## O que o projeto demonstra

| Rota | Implementação | Resultado com `admin' --` |
|------|---------------|---------------------------|
| `/login-inseguro` | Query SQL montada por concatenação de strings | `200` (ataque funciona) |
| `/login` | Query parametrizada, senha com hash, limite de tentativas e emissão de token JWT | `401` (ataque barrado) |
| `/perfil` | Rota protegida: exige token JWT válido no cabeçalho `Authorization` | `401` sem token válido |

## Controles de segurança implementados

- **SQL Injection:** a rota segura usa query parametrizada.
- **Armazenamento de senha:** hash com `werkzeug.security`. A tabela `users_inseguro`, em texto puro, existe só para o laboratório de SQL Injection.
- **Força bruta:** após 5 tentativas erradas para o mesmo usuário, a rota `/login` responde `429`.
- **Autenticação por token:** `/login` devolve um JWT (HS256) com expiração de 15 minutos. A rota `/perfil` só responde `200` com um token válido.
- **Cabeçalhos de segurança HTTP:** `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy` e `Cache-Control` em todas as respostas.

## Tecnologias

Python 3.12, Flask, SQLite, PyJWT, pytest

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
