# Security QA API (em andamento)

Projeto de estudo de **Security QA**: uma API Flask com duas versões do mesmo login, uma **propositalmente vulnerável** a SQL Injection e outra segura, com testes automatizados que provam a diferença entre as duas.

> **Aviso:** a rota `/login-inseguro` é vulnerável de propósito, para fins educacionais. Rode apenas localmente (o servidor já escuta só em `127.0.0.1`) e nunca publique essa API na internet.

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
```

A API sobe em `http://127.0.0.1:5000`.

## Exemplo de ataque

```bash
curl -i -X POST http://127.0.0.1:5000/login-inseguro \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'"'"' --","password":"qualquer"}'
```

## Exemplo de uso do token

```bash
# 1. fazer login e copiar o valor de "access_token"
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. acessar a rota protegida
curl -i http://127.0.0.1:5000/perfil \
  -H "Authorization: Bearer COLE_O_TOKEN_AQUI"
```

## Testes

```bash
pytest -v
```

Os testes cobrem:

- login válido e senha errada
- payloads de SQL Injection nas duas rotas
- aspas simples sem erro 500 e validação de campos vazios
- armazenamento de senha com hash
- bloqueio após várias tentativas erradas
- cabeçalhos de segurança nas respostas (inclusive de erro)
- JWT: sem token, token válido, adulterado, expirado, assinado por outra chave e com algoritmo `none`

Eles usam um banco temporário, então não alteram o `users.db`.

## Limitações conhecidas (próximos passos)

- O contador de tentativas fica em memória (reinicia com o servidor) e não expira
- O token JWT não tem logout nem revogação: um token roubado vale até expirar
- A chave do JWT tem um valor padrão só para estudo; em produção deve vir da variável de ambiente `JWT_SECRET_KEY`
- Sem `Strict-Transport-Security`, pois a API roda em HTTP local
