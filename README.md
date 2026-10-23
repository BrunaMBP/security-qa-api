# Security QA API

![Testes](https://github.com/BrunaMBP/security-qa-api/actions/workflows/tests.yml/badge.svg)

Projeto de estudo de **Security QA**, desenvolvido com Python e Flask para demonstrar vulnerabilidades comuns em APIs, implementar controles de segurança e validar seu comportamento por meio de testes automatizados.

A aplicação disponibiliza uma rota de login propositalmente vulnerável a SQL Injection e outra com implementação segura, permitindo comparar os resultados dos ataques simulados.

> **Aviso:** a rota `/login-inseguro` é intencionalmente vulnerável e existe exclusivamente para fins educacionais. Execute este projeto apenas em ambiente local controlado. Não utilize credenciais reais nem exponha a aplicação à internet.

## Objetivos do projeto

- Demonstrar o impacto de SQL Injection.
- Validar a eficácia de consultas SQL parametrizadas.
- Verificar o armazenamento seguro de senhas.
- Testar autenticação e autorização com JWT.
- Validar controles contra tentativas repetidas de login.
- Verificar cabeçalhos de segurança HTTP.
- Automatizar testes funcionais e de segurança com pytest.
- Executar a aplicação em um container Docker.

## Funcionalidades e controles de segurança

| Controle | Implementação |
|---|---|
| SQL Injection | Comparação entre uma consulta vulnerável e outra parametrizada |
| Armazenamento de senhas | Hash de senhas com Werkzeug |
| Tentativas de login | Bloqueio após cinco tentativas incorretas para o mesmo usuário |
| Autenticação | JWT assinado com HS256 |
| Expiração do token | Validade de 15 minutos |
| Autorização | Rota de perfil protegida por token |
| Cabeçalhos HTTP | Configuração de cabeçalhos de segurança nas respostas |
| Testes automatizados | Suíte de testes com pytest |
| Containerização | Dockerfile baseado em Python 3.12 slim |

## Endpoints

| Endpoint | Método | Descrição |
|---|---|---|
| `/login-inseguro` | POST | Login intencionalmente vulnerável a SQL Injection |
| `/login` | POST | Login com consulta parametrizada e validação de credenciais |
| `/perfil` | GET | Retorna o perfil do usuário autenticado mediante JWT válido |

### Comparação de SQL Injection

| Cenário | Resultado esperado |
|---|---|
| Tentativa de SQL Injection em `/login-inseguro` | A vulnerabilidade pode permitir autenticação indevida |
| Tentativa de SQL Injection em `/login` | A consulta parametrizada impede que a entrada seja interpretada como parte do comando SQL |

Os resultados dependem das condições do laboratório e das entradas utilizadas.

## Autenticação JWT

Após um login válido em `/login`, a API retorna um token JWT assinado com HS256 e validade de 15 minutos.

O token deve ser enviado no cabeçalho `Authorization` para acessar a rota protegida.

Exemplo de cabeçalho:

```http
Authorization: Bearer SEU_TOKEN_JWT
```

A rota `/perfil` deve rejeitar requisições sem token ou com token inválido, adulterado ou expirado.

## Cabeçalhos de segurança HTTP

A aplicação configura os seguintes cabeçalhos:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`
- `Referrer-Policy: no-referrer`
- `Cache-Control: no-store`

A suíte automatizada verifica a presença desses cabeçalhos nas respostas testadas, inclusive em determinados cenários de erro.

## Tecnologias utilizadas

- Python 3.12
- Flask
- SQLite
- PyJWT
- pytest
- Docker
- Git e GitHub

## Como executar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/BrunaMBP/security-qa-api.git
cd security-qa-api
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar os testes automatizados

```bash
pytest -v
```

**Resultado registrado durante o desenvolvimento:** 24 testes aprovados em 2,40 segundos.

Esse resultado corresponde à execução local realizada durante o desenvolvimento. A execução no Docker e o resultado do GitHub Actions devem ser verificados separadamente.

### 5. Iniciar a aplicação

```bash
python app.py
```

Por padrão, a aplicação é iniciada em `127.0.0.1:5000`, conforme a configuração local.

## Como executar com Docker

### 1. Construir a imagem

Na raiz do repositório, execute:

```bash
docker build -t security-qa-api .
```

### 2. Iniciar o container

Para o laboratório local, configure uma chave JWT de teste e publique a porta somente no endereço de loopback:

```bash
docker run --rm --name security-qa-api-test \
  -e JWT_SECRET_KEY='chave-de-teste-local-12345678901234567890' \
  -p 127.0.0.1:5000:5000 \
  security-qa-api
```

A chave acima é exclusiva para testes locais. Não a utilize em produção.

Mantenha o terminal aberto enquanto o container estiver em execução.

### 3. Verificar a rota protegida

Em outro terminal:

```bash
curl -i http://127.0.0.1:5000/perfil
```

Sem um token válido, o resultado esperado é `401 Unauthorized`.

Para testar o login e o acesso autenticado, utilize credenciais válidas do ambiente de teste e envie o token retornado no cabeçalho `Authorization`.

> **Observação:** o Docker utiliza um banco de dados dentro do container. A inicialização do banco e a disponibilidade de um usuário de teste precisam ser confirmadas antes de executar os testes de login.

## Testes automatizados

A suíte atual contém **24 testes automatizados**, distribuídos entre autenticação e controles de segurança.

Os cenários incluem:

- Login válido e inválido.
- SQL Injection na rota vulnerável.
- Bloqueio de SQL Injection na rota segura.
- Validação de campos vazios.
- Verificação de hash de senhas.
- Verificação de cabeçalhos de segurança.
- Acesso a rota protegida sem token.
- Autenticação com JWT válido.
- Rejeição de token adulterado.
- Rejeição de token expirado.
- Rejeição de token assinado com outra chave.
- Rejeição de token com algoritmo `none`.

Última execução local registrada:

```text
24 passed in 2.40s
```

Os testes demonstram o comportamento esperado nos cenários cobertos, mas não garantem a ausência de todas as vulnerabilidades.

## Estrutura do projeto

```text
security-qa-api/
├── app.py
├── database.py
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── .dockerignore
├── README.md
└── tests/
    ├── test_auth.py
    └── test_security.py
```

## Próximas melhorias

- Configurar e validar a execução dos testes no GitHub Actions.
- Ampliar os testes negativos de autenticação e autorização.
- Integrar testes dinâmicos de segurança com OWASP ZAP.
- Avaliar a implementação de rate limiting com armazenamento apropriado.
- Melhorar a gestão de segredos e a configuração para ambientes diferentes.
- Avaliar persistência e isolamento do banco de dados no Docker.

## Objetivo profissional

Este projeto faz parte dos meus estudos em **Quality Assurance com foco em segurança de aplicações**, combinando testes funcionais, testes de API, automação e validação de controles de segurança.

O objetivo é demonstrar, na prática, como a atuação de QA pode contribuir para identificar vulnerabilidades, validar correções e reduzir riscos durante o desenvolvimento de software.