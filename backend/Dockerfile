# ==============================================================================
# FoodCommerce AI Dashboard - Backend Dockerfile
# ==============================================================================
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e força flush imediato no stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e os datasets CSV
COPY . .

# Porta exposta (configurável via variável de ambiente PORT)
EXPOSE 5000

# Execução com servidor WSGI de produção (Gunicorn)
# --workers 2 e --timeout 120 para permitir o carregamento do modelo e dos dados
CMD exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app

