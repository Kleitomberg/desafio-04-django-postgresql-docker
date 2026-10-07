# Desafio 04 — Django + PostgreSQL + Docker

Aplicação Django containerizada com PostgreSQL, utilizando Docker Network para comunicação entre os containers e volume nomeado para persistência dos dados.

## 🎯 Objetivo

Evoluir a aplicação do Desafio 03, separando a aplicação Django do banco de dados PostgreSQL.

Neste desafio foram praticados:

- Dockerfile para aplicação Django
- Gunicorn
- PostgreSQL com imagem oficial
- Docker Network
- Comunicação entre containers
- Variáveis de ambiente
- Volumes nomeados
- Persistência de dados
- Django ORM e migrations
- `psycopg`
- `collectstatic`
- WhiteNoise
- Django Admin em ambiente containerizado

---

## 🏗️ Arquitetura

```text
                    Docker Network
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       app_django              postgres-desafio4
       Django + Gunicorn           PostgreSQL
          :8000                       :5432
             │                         │
             │                         ▼
             │                desafio4_postgres_data
             │                    (Volume)
             │
             ▼
        Mac localhost
           :8008
```

O Django e o PostgreSQL executam em containers separados e se comunicam através da mesma rede Docker.

---

## 🛠️ Tecnologias

- Python 3.12
- Django 6.1.2
- Gunicorn 23.0.0
- PostgreSQL 18.6
- Psycopg 3
- WhiteNoise
- Docker

---

## 📁 Estrutura

```text
desafio4/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── static/
```

> O arquivo `.env` não deve ser versionado no Git.

---

# 🐘 PostgreSQL

O PostgreSQL utiliza a imagem oficial:

```bash
postgres:18.6
```

Container:

```text
postgres-desafio4
```

Banco:

```text
desafio4_db
```

Usuário:

```text