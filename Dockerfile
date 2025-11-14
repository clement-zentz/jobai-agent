# Dockerfile

FROM python:3.12-slim

# Install UV
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copier uniquement les fichiers de config de dépendances
COPY pyproject.toml uv.lock ./

# install dependencies using uv sync
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
