# Security QA API

Projeto de estudo de **Security QA**: uma API Flask com duas versões do mesmo login, uma **propositalmente vulnerável** a SQL Injection e outra segura, com testes automatizados que provam a diferença entre as duas.

> **Aviso:** a rota `/login-inseguro` é vulnerável de propósito, para fins educacionais. Rode apenas localmente (o servidor já escuta só em `127.0.0.1`) e nunca publique essa API na internet.

## O que o projeto demonstra

| Rota | Implementação | Resultado com `admin' --` |
|------|---------------|---------------------------|
| `/login-inseguro` | Query SQL montada por concatenação de strings | `200` (ataque funciona) |
| `/login` | Query parametrizada | `401` (ataque barrado) |

## Tecnologias

Python 3.12, Flask, SQLite, pytest

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

## Testes

```bash
pytest -v
```

Os testes cobrem login válido, senha errada, payloads de SQL Injection nas duas rotas, aspas simples sem erro 500 e validação de campos vazios. Eles usam um banco temporário, então não alteram o `users.db`.

## Limitações conhecidas (próximos passos)

- Senhas armazenadas em texto puro (trocar por hash, por exemplo bcrypt)
- Sem limite de tentativas de login (testar força bruta)
- Sem cabeçalhos de segurança HTTP
- Sem autenticação por token
