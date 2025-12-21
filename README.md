# Pomodoro Timer - Aplicação Clusterizada

Aplicação de timer Pomodoro com arquitetura de microsserviços usando Docker Swarm.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Executando Localmente](#executando-localmente)
- [Deploy com Docker Swarm](#deploy-com-docker-swarm)
- [Testes de Carga](#testes-de-carga)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## 🎯 Sobre o Projeto

Timer Pomodoro simples com:
- Botão Iniciar
- Botão Pausar
- Botão Recomeçar
- Exibição do tempo decorrido em tempo real
- Persistência no banco de dados PostgreSQL

---

## 🏗️ Arquitetura
```
┌─────────────────────────────────────┐
│         Docker Swarm Cluster        │
├─────────────────────────────────────┤
│                                     │
│  PostgreSQL (1 réplica)             │
│  └─ Banco de dados                  │
│                                     │
│  Backend FastAPI (3 réplicas)       │
│  ├─ API REST                        │
│  ├─ Lógica de negócio               │
│  └─ Conexão com banco               │
│                                     │
│  Frontend React (2 réplicas)        │
│  └─ Interface do usuário            │
│                                     │
│  Load Balancer (automático)         │
│  └─ Docker Swarm routing mesh       │
└─────────────────────────────────────┘
```

**Stack:**
- Backend: Python + FastAPI + SQLAlchemy
- Frontend: React
- Banco: PostgreSQL 15
- Orquestração: Docker Swarm

---

## ✅ Pré-requisitos

### Para Desenvolvimento Local:

- Python 3.10+
- Node.js 18+
- PostgreSQL 15
- pip
- npm

### Para Docker Swarm (Recomendado):

- Docker 20.10+
- Docker Compose 1.29+
- VM Linux (Ubuntu 22.04 LTS recomendado)
  - RAM: 4GB mínimo
  - CPU: 2 cores
  - Disco: 20GB

---

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd pomodoro-cluster
```

### 2. Estrutura de pastas
```
pomodoro-cluster/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── docker-stack.yml
└── README.md
```

---

## 💻 Executando Localmente

### Backend
```bash
cd backend

# Criar ambiente virtual (opcional)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
echo "DATABASE_URL=postgresql://pomodoro_user:pomodoro_pass@localhost:5433/pomodoro_db" > .env

# Rodar servidor
python3 -m uvicorn main:app --reload --port 8000
```

Acesse: http://localhost:8000/docs

### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Rodar servidor
npm start
```

Acesse: http://localhost:3000

### Banco de Dados (Docker)
```bash
docker run -d \
  --name pomodoro_db \
  -e POSTGRES_USER=pomodoro_user \
  -e POSTGRES_PASSWORD=pomodoro_pass \
  -e POSTGRES_DB=pomodoro_db \
  -p 5433:5432 \
  postgres:15
```

---

## 🐳 Deploy com Docker Compose

### Subir todos os serviços
```bash
# Build das imagens
docker-compose build

# Subir containers
docker-compose up -d

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar tudo
docker-compose down
```

### Escalonamento com docker-compose
```bash
# Subir com múltiplas réplicas
docker-compose up -d --scale backend=3 --scale frontend=2
```

---

## 🐝 Deploy com Docker Swarm

### 1. Preparar VM Linux

#### Instalação do Docker na VM Ubuntu
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar para aplicar
exit
# (faça login novamente)

# Verificar instalação
docker --version
```

### 2. Inicializar Swarm
```bash
# Inicializar Swarm
docker swarm init --advertise-addr <IP_DA_VM>

# Verificar nodes
docker node ls
```

### 3. Build das imagens
```bash
# Transferir projeto para a VM (via git, scp, etc)

cd pomodoro-cluster

# Build backend
docker build -t pomodoro-backend:latest ./backend

# Build frontend
docker build -t pomodoro-frontend:latest ./frontend
```

### 4. Deploy da Stack
```bash
# Deploy
docker stack deploy -c docker-stack.yml pomodoro

# Verificar serviços
docker stack services pomodoro

# Ver detalhes
docker stack ps pomodoro

# Logs de um serviço
docker service logs pomodoro_backend

# Remover stack
docker stack rm pomodoro
```

### 5. Escalando Serviços
```bash
# Escalar backend para 5 réplicas
docker service scale pomodoro_backend=5

# Escalar frontend para 3 réplicas
docker service scale pomodoro_frontend=3

# Verificar
docker service ls
```

---

## 📊 Testes de Carga

### Instalação do Apache Bench
```bash
sudo apt-get install apache2-utils
```

### Testes Básicos
```bash
# 1000 requisições, 10 simultâneas
ab -n 1000 -c 10 http://localhost:8000/timer/elapsed

# 5000 requisições, 50 simultâneas
ab -n 5000 -c 50 http://localhost:8000/timer/elapsed

# Com POST (iniciar timer)
ab -n 1000 -c 10 -p /dev/null -T application/json http://localhost:8000/timer/start
```

### Teste com Locust (Avançado)
```bash
# Instalar
pip install locust

# Criar arquivo locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class PomodoroUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_elapsed(self):
        self.client.get("/timer/elapsed")
    
    @task(1)
    def start_timer(self):
        self.client.post("/timer/start")
    
    @task(1)
    def pause_timer(self):
        self.client.post("/timer/pause")
EOF

# Rodar
locust -f locustfile.py --host=http://localhost:8000
```

Acesse: http://localhost:8089

---

## 📁 Estrutura do Projeto

### Backend (FastAPI)

**Endpoints:**

- `GET /` - Health check
- `POST /timer/start` - Inicia o timer
- `POST /timer/pause` - Pausa o timer
- `POST /timer/reset` - Reseta o timer
- `GET /timer/elapsed` - Retorna tempo decorrido

**Arquivos principais:**

- `main.py` - Endpoints da API
- `database.py` - Configuração do banco
- `models.py` - Modelo SQLAlchemy
- `requirements.txt` - Dependências Python

### Frontend (React)

**Componentes:**

- Timer display
- Botões de controle (Iniciar, Pausar, Recomeçar)
- Status indicator

**Arquivos principais:**

- `src/App.js` - Componente principal
- `src/App.css` - Estilos

---

## 🔧 Configurações

### Variáveis de Ambiente

**Backend (.env):**
```env
DATABASE_URL=postgresql://pomodoro_user:pomodoro_pass@postgres:5432/pomodoro_db
```

**Docker Compose:**
```yaml
POSTGRES_USER=pomodoro_user
POSTGRES_PASSWORD=pomodoro_pass
POSTGRES_DB=pomodoro_db
```

### Portas

- Frontend: `3000`
- Backend: `8000`
- PostgreSQL: `5433` (externa) / `5432` (interna)

---

## 🐛 Troubleshooting

### Erro CORS no Frontend

Certifique-se que o backend tem CORS configurado:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Containers não sobem no Swarm (WSL)

Docker Swarm tem limitações no WSL. Soluções:

1. Use Docker Desktop
2. Use VM Linux real
3. Use docker-compose com `--scale`

### Banco não conecta

Verifique:
- PostgreSQL está rodando: `docker ps`
- Porta correta no DATABASE_URL
- Credenciais corretas

---

## 📝 Próximos Passos

- [ ] Adicionar autenticação de usuários
- [ ] Implementar histórico de sessões
- [ ] Adicionar notificações/alarmes
- [ ] Implementar Nginx como API Gateway
- [ ] Adicionar Redis para cache
- [ ] Configurar CI/CD
- [ ] Monitoramento com Prometheus/Grafana

---


## 📄 Licença

Este projeto é para fins educacionais.
