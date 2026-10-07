# 🐳 Desafio 04 — Django + PostgreSQL + Docker

Evolução do ambiente Dockerizado desenvolvido no Desafio 03, agora introduzindo um banco de dados PostgreSQL em um container separado.

O objetivo deste desafio foi sair de uma aplicação Django isolada e construir uma pequena infraestrutura composta por **aplicação + banco de dados**, utilizando recursos nativos do Docker para comunicação, persistência e configuração.

> **Importante:** neste desafio, a infraestrutura foi criada propositalmente utilizando comandos Docker individuais. O Docker Compose será introduzido no próximo desafio para automatizar essa configuração.

---

## 🎯 Objetivo

Construir um ambiente no qual:

- o Django execute em seu próprio container;
- o PostgreSQL execute em um container separado;
- Django e PostgreSQL se comuniquem através de uma Docker Network;
- as credenciais e configurações sejam fornecidas por variáveis de ambiente;
- os dados do PostgreSQL sejam persistidos através de um volume nomeado;
- o Django utilize Gunicorn para execução;
- as migrations sejam aplicadas no PostgreSQL;
- os arquivos estáticos sejam coletados e servidos corretamente;
- o Django Admin funcione dentro do ambiente Docker.

---

## 🏗️ Arquitetura

```text
                         Docker Host
                              │
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    │  desafio4-network │
                    │                   │
                    └─────────┬─────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
        ┌──────────────┐              ┌──────────────┐
        │  app_django  │              │ PostgreSQL   │
        │              │              │              │
        │ Django       │              │ postgres:18.6│
        │ Gunicorn     │              │              │
        │              │              │ :5432        │
        │ :8000        │              └──────┬───────┘
        └──────┬───────┘                     │
               │                             │
               │                             ▼
               │                    ┌──────────────────┐
               │                    │ desafio4_        │
               │                    │ postgres_data    │
               │                    │                  │
               │                    │ Persistent Data  │
               │                    └──────────────────┘
               │
               ▼
        localhost:8008
```

### Fluxo da aplicação

```text
Browser
   │
   │ localhost:8008
   ▼
Docker Host
   │
   │ :8008 → :8000
   ▼
Django Container
   │
   │ Docker Network
   │ DB_HOST=postgres-desafio4
   ▼
PostgreSQL Container
   │
   ▼
Named Volume
```

---

# 🧩 O que mudou em relação ao Desafio 03?

No desafio anterior, a aplicação era praticamente autossuficiente:

```text
┌───────────────────────┐
│ Django Container      │
│                       │
│ Django                │
│ Gunicorn              │
│ SQLite                │
└───────────────────────┘
```

Agora a aplicação passa a ter uma arquitetura mais próxima de um ambiente real:

```text
┌─────────────────┐          ┌──────────────────┐
│ Django          │          │ PostgreSQL       │
│                 │ ───────► │                  │
│ Gunicorn        │ Network  │ Banco de dados   │
└─────────────────┘          └────────┬─────────┘
                                      │
                                      ▼
                               Volume persistente
```

Isso introduz três conceitos fundamentais do Docker:

- **Network**
- **Volume**
- **Container-to-container communication**

---

# 🐘 PostgreSQL

O banco de dados utiliza a imagem oficial:

```text
postgres:18.6
```

O container foi criado com:

```bash
docker run \
  --name postgres-desafio4 \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=desafio4_db \
  -e POSTGRES_USER=admin \
  -d \
  postgres:18.6
```

Foram utilizadas as variáveis disponibilizadas pela própria imagem do PostgreSQL:

| Variável | Função |
|---|---|
| `POSTGRES_DB` | Nome do banco inicial |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do usuário |

---

# 🌐 Docker Network

Foi criada uma rede dedicada para permitir a comunicação entre os containers:

```bash
docker network create desafio4-network
```

O PostgreSQL foi conectado à rede:

```bash
docker network connect desafio4-network postgres-desafio4
```

O Django também foi executado nessa mesma rede.

## Por que não usar `localhost`?

Dentro do container Django:

```text
localhost
```

significa:

```text
o próprio container Django
```

Portanto, o Django não encontraria o PostgreSQL utilizando:

```env
DB_HOST=localhost
```

Em vez disso, foi utilizado o nome do container:

```env
DB_HOST=postgres-desafio4
```

O Docker resolve esse nome dentro da rede:

```text
app_django
     │
     │ DB_HOST=postgres-desafio4
     ▼
postgres-desafio4
```

Esse conceito é fundamental para comunicação entre containers.

---

# 💾 Persistência com Docker Volume

Para evitar que os dados do PostgreSQL dependessem exclusivamente do ciclo de vida do container, foi criado um volume nomeado:

```bash
docker volume create desafio4_postgres_data
```

O volume representa uma camada persistente para os dados do banco.

```text
PostgreSQL Container
        │
        ▼
desafio4_postgres_data
        │
        ▼
      Dados
```

Dessa forma, podemos remover e recriar o container PostgreSQL sem necessariamente perder os dados armazenados no volume.

### Conceito importante

Container e dados possuem ciclos de vida diferentes:

```text
Container
  └── pode ser destruído/recriado

Volume
  └── continua existindo
```

Essa separação é uma das principais vantagens da utilização de volumes no Docker.

---

# ⚙️ Configuração do Django

O Django foi configurado para utilizar PostgreSQL através das variáveis de ambiente:

```env
DB_NAME=desafio4_db
DB_USER=admin
DB_PASSWORD=mysecretpassword
DB_HOST=postgres-desafio4
DB_PORT=5432
```

A configuração do banco utiliza:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}
```

### Por que utilizar variáveis de ambiente?

A aplicação não precisa conhecer diretamente:

- nome do banco;
- usuário;
- senha;
- endereço do banco;
- porta.

Isso permite alterar a configuração entre ambientes sem alterar o código da aplicação.

---

# 📦 Dependências

O projeto utiliza:

```text
Django==6.1.2
gunicorn==23.0.0
psycopg[binary]==3.3.6
whitenoise==6.12.0
```

### Psycopg

O Django precisa de um driver para conversar com PostgreSQL.

Neste projeto foi utilizado o Psycopg 3:

```text
psycopg[binary]
```

O uso do extra `binary` evita a necessidade de instalar e configurar manualmente algumas dependências nativas do PostgreSQL no container.

---

# 🐳 Dockerfile

A aplicação continua utilizando uma imagem oficial do Python:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install -r ./requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "config.wsgi:application" ]
```

## Ordem do build

```text
Dockerfile
    │
    ├── FROM Python 3.12
    │
    ├── WORKDIR /app
    │
    ├── COPY requirements.txt
    │
    ├── pip install
    │
    ├── COPY aplicação
    │
    ├── collectstatic
    │
    ├── EXPOSE 8000
    │
    └── Gunicorn
```

A separação do `requirements.txt` antes do restante da aplicação também permite aproveitar o cache das camadas do Docker quando apenas o código da aplicação é alterado.

---

# 📁 Arquivos estáticos

Durante o build da imagem:

```bash
python manage.py collectstatic --noinput
```

O Django coleta os arquivos estáticos para:

```text
/app/static/
```

Por exemplo:

```text
/app/static/admin/
```

Isso inclui os arquivos utilizados pelo Django Admin:

```text
admin/
├── css/
├── js/
└── img/
```

---

# 🧱 WhiteNoise

O projeto utiliza WhiteNoise para servir os arquivos estáticos diretamente pela aplicação.

A biblioteca está instalada em:

```text
whitenoise==6.12.0
```

e configurada no `MIDDLEWARE`.

O fluxo passa a ser:

```text
Browser
   │
   │ /static/admin/css/base.css
   ▼
Gunicorn
   │
   ▼
WhiteNoise
   │
   ▼
/app/static/admin/css/base.css
```

### Problema encontrado durante o desafio

Inicialmente, o Django Admin carregava o HTML, mas aparecia sem CSS e JavaScript.

Os arquivos existiam no container:

```text
/app/static/admin/
```

porém o Django retornava:

```text
Not Found: /static/admin/css/base.css
Not Found: /static/admin/js/theme.js
```

A causa era que o WhiteNoise estava instalado, mas ainda não estava configurado no `MIDDLEWARE`.

Após a configuração, os arquivos estáticos passaram a ser servidos corretamente.

Esse problema foi importante para entender a diferença entre:

```text
arquivo existir no container
```

e:

```text
arquivo estar disponível através de uma URL HTTP
```

---

# 🚀 Build da imagem

```bash
docker build -t desafio4-django .
```

A imagem criada:

```text
desafio4-django
```

---

# ▶️ Executando o Django

O container foi executado utilizando:

```bash
docker run -d \
  --name app_django \
  -p 8008:8000 \
  --env-file .env \
  --network desafio4-network \
  desafio4-django
```

### Portas

A aplicação utiliza:

```text
Host       Container
8008   →   8000
```

Portanto:

```text
http://localhost:8008
```

acessa:

```text
Gunicorn :8000
```

dentro do container.

---

# 🔄 Gunicorn

O Django não é executado utilizando:

```bash
python manage.py runserver
```

dentro do container.

A aplicação é executada através do Gunicorn:

```text
Gunicorn
   │
   ▼
config.wsgi:application
   │
   ▼
Django
```

Comando utilizado no Dockerfile:

```dockerfile
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "config.wsgi:application" ]
```

### Por que `0.0.0.0`?

O Gunicorn precisa escutar em todas as interfaces de rede disponíveis dentro do container.

```text
0.0.0.0:8000
```

não significa que o navegador deve acessar `0.0.0.0`.

O acesso externo é feito através do mapeamento:

```text
localhost:8008
       ↓
container:8000
```

---

# 🗄️ Migrations

As migrations foram executadas dentro do container Django:

```bash
docker exec -it app_django python manage.py migrate
```

O Django passou a criar as tabelas no PostgreSQL.

Através do cliente `psql`:

```bash
docker exec -it postgres-desafio4 psql -U admin -d desafio4_db
```

é possível verificar:

```sql
\dt
```

Entre as tabelas criadas:

```text
auth_group
auth_permission
auth_user
auth_user_groups
auth_user_user_permissions
django_admin_log
django_content_type
django_migrations
django_session
```

Isso confirmou que:

```text
Django
   ↓
Docker Network
   ↓
PostgreSQL
   ↓
desafio4_db
```

estava funcionando corretamente.

---

# 👤 Django Admin

Foi criado um superusuário através do container:

```bash
docker exec -it app_django python manage.py createsuperuser
```

O painel pode ser acessado em:

```text
http://localhost:8008/admin/
```

O funcionamento do Admin também serviu como teste integrado da aplicação:

```text
Browser
   ↓
Django
   ↓
Gunicorn
   ↓
PostgreSQL
   ↓
Volume
```

Além disso, o carregamento correto do CSS/JavaScript confirmou o funcionamento do WhiteNoise.

---

# 🔍 Comandos úteis

### Containers

```bash
docker ps
```

```bash
docker ps -a
```

### Logs

```bash
docker logs app_django
```

```bash
docker logs -f app_django
```

### Entrar no Django

```bash
docker exec -it app_django /bin/bash
```

### PostgreSQL

```bash
docker exec -it postgres-desafio4 psql -U admin -d desafio4_db
```

### Networks

```bash
docker network ls
```

```bash
docker network inspect desafio4-network
```

### Volumes

```bash
docker volume ls
```

```bash
docker volume inspect desafio4_postgres_data
```

---

# 🧪 Testes realizados

Durante o desafio foram realizados testes para validar cada camada da infraestrutura.

### PostgreSQL

- [x] Container criado
- [x] Banco `desafio4_db` criado
- [x] Usuário `admin` criado
- [x] PostgreSQL iniciou corretamente
- [x] PostgreSQL aceitando conexões na porta `5432`

### Docker

- [x] Imagem Django criada
- [x] Container Django criado
- [x] Containers conectados à mesma Network
- [x] Volume nomeado criado
- [x] Comunicação entre containers validada

### Django

- [x] Django conectado ao PostgreSQL
- [x] Psycopg funcionando
- [x] Migrations executadas
- [x] Tabelas criadas no PostgreSQL
- [x] Superusuário criado
- [x] Django Admin acessível

### Static Files

- [x] `collectstatic` executado durante o build
- [x] Arquivos do Admin presentes em `/app/static`
- [x] Problema de arquivos estáticos identificado
- [x] WhiteNoise configurado
- [x] CSS e JavaScript do Admin carregando corretamente

---

# 🧠 Principais aprendizados

## 1. Container não é a mesma coisa que imagem

```text
Dockerfile
    ↓
docker build
    ↓
Imagem
    ↓
docker run
    ↓
Container
```

Alterar o código/configuração da aplicação e executar apenas `docker build` não altera um container que já está rodando.

É necessário recriar o container utilizando a nova imagem.

---

## 2. Containers precisam de uma rede para conversar

O Django não acessa o PostgreSQL através de `localhost`.

A comunicação acontece através da Docker Network e do nome do container:

```text
app_django
     │
     ▼
postgres-desafio4
```

---

## 3. Container e dados possuem ciclos de vida diferentes

O container PostgreSQL pode ser removido enquanto o volume continua existindo.

```text
Container → descartável
Volume    → persistente
```

Essa separação permite recriar a infraestrutura sem necessariamente perder os dados.

---

## 4. `EXPOSE` não publica uma porta

No Dockerfile:

```dockerfile
EXPOSE 8000
```

apenas documenta a porta utilizada pelo container.

Quem cria o acesso do host para o container é:

```bash
-p 8008:8000
```

---

## 5. `collectstatic` não significa que os arquivos estão sendo servidos

O `collectstatic` apenas reúne os arquivos:

```text
/app/static/
```

Ainda é necessário ter uma estratégia para disponibilizá-los através de HTTP.

Neste projeto:

```text
WhiteNoise
```

foi utilizado para essa finalidade.

---

# 📚 Conceitos Docker praticados

| Conceito | Aplicação no desafio |
|---|---|
| Image | `desafio4-django` |
| Container | `app_django` / `postgres-desafio4` |
| Network | `desafio4-network` |
| Volume | `desafio4_postgres_data` |
| Port Mapping | `8008:8000` |
| Environment Variables | `.env` |
| Official Image | `postgres:18.6` |
| Dockerfile | Build do Django |
| `docker exec` | Administração dos containers |
| `docker logs` | Diagnóstico |
| Container DNS | `postgres-desafio4` |
| Persistence | PostgreSQL + volume |

---

# 🏁 Resultado final

Ao final do desafio, a aplicação deixou de depender de um banco local e passou a utilizar uma arquitetura composta por múltiplos containers:

```text
                    Docker
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        Django/Gunicorn      PostgreSQL
             │                   │
             │                   ▼
             │              Volume Docker
             │
             ▼
         WhiteNoise
             │
             ▼
        Static Files
```

O ambiente agora possui:

- Django em container próprio;
- Gunicorn como servidor WSGI;
- PostgreSQL em container separado;
- comunicação via Docker Network;
- persistência via volume nomeado;
- configuração através de variáveis de ambiente;
- migrations executadas no PostgreSQL;
- Django Admin funcionando;
- arquivos estáticos coletados e servidos pelo WhiteNoise.

---

# 🚀 Próximo passo — Desafio 05

No próximo desafio, a infraestrutura criada manualmente será transformada em uma configuração declarativa utilizando **Docker Compose**.

O objetivo será substituir diversos comandos manuais por uma única definição capaz de criar:

```text
Django
PostgreSQL
Network
Volume
```

através de:

```bash
docker compose up
```

Assim, o próximo desafio introduzirá o conceito de **orquestração local de múltiplos containers**.