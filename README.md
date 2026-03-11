# 🚀 AI News API - Documentação

API Django REST para buscar notícias sobre IA em tempo real.

## 📋 Endpoints

### 1. Health Check
```
GET /api/health/
```

**Resposta:**
```json
{
  "status": "ok"
}
```

### 2. Buscar Notícias
```
GET /api/news/
```

**Resposta:**
```json
{
  "timestamp": "2026-02-06T21:02:08.857938",
  "total_news": 139,
  "news": [
    {
      "title": "ChatGPT GPT-4o users are raging...",
      "description": "...",
      "url": "https://...",
      "source": "Mashable",
      "published_date": "Fri, 06 Feb 2026 18:07:06 GMT",
      "topic": "ChatGPT"
    }
  ]
}
```

## 🚀 Como Usar

### Iniciar o servidor

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor
python manage.py runserver 8000
```

O servidor estará disponível em: `http://localhost:8000`

### Testar endpoints

```bash
# Health check
curl http://localhost:8000/api/health/

# Buscar notícias
curl http://localhost:8000/api/news/
```

### Usar em produção

Para produção, use um servidor WSGI como Gunicorn:

```bash
# Instalar Gunicorn
pip install gunicorn

# Iniciar servidor
gunicorn api.wsgi:application --bind 0.0.0.0:8000
```

## 🔌 Integração com n8n

### Opção 1: HTTP Request Node

1. Adicione um **HTTP Request Node**
2. Configure:
   - **Method**: GET
   - **URL**: `http://localhost:8000/api/news/`
   - **Response Format**: JSON

### Opção 2: Workflow Completo

```
[Schedule Trigger (Cron)]
  ↓
[HTTP Request: GET /api/news/]
  ↓
[Filter/Transform Data]
  ↓
[Slack Message]
```

## ⚙️ Configuração

### Tópicos de busca

Edite `news/news_fetcher.py`:

```python
TOPICOS = [
    'artificial intelligence',
    'Claude AI',
    'ChatGPT',
    'Anthropic',
    # ... adicione mais tópicos
]
```

### Período de busca

```python
MAX_RESULTS = 10  # notícias por tópico
PERIOD = '1d'     # '1d', '7d', '30d'
```

## 🛡️ Segurança

**IMPORTANTE**: Antes de colocar em produção:

1. Altere o `SECRET_KEY` em `api/settings.py`
2. Configure `DEBUG = False`
3. Configure `ALLOWED_HOSTS` corretamente
4. Use variáveis de ambiente para dados sensíveis
5. Configure CORS adequadamente

```python
# api/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://seu-n8n.com",
]
```

## 📊 Performance

- **Busca paralela**: 8 workers simultâneos
- **Tempo de resposta**: ~3-5 segundos
- **Notícias por requisição**: ~100-150 (sem duplicatas)

## 🐛 Troubleshooting

### Erro de porta em uso
```bash
# Matar processos usando porta 8000
lsof -ti:8000 | xargs kill -9
```

### Erro de importação
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### CORS Error
Verifique se `corsheaders` está em `INSTALLED_APPS` e `MIDDLEWARE` no `settings.py`

## 📝 Logs

Para ver logs do servidor:
```bash
python manage.py runserver --verbosity 2
```

## 🔄 Deploy

### Docker (opcional)

Crie um `Dockerfile`:
```dockerfile
FROM python:3.14-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```bash
docker build -t ai-news-api .
docker run -p 8000:8000 ai-news-api
```
