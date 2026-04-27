# ---------- STAGE 1: Builder ----------
FROM python:3.11-alpine AS builder

WORKDIR /app

# Installer les dépendances de compilation
RUN apk add --no-cache gcc musl-dev libpq-dev

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- STAGE 2: Image ultra-légère ----------
FROM python:3.11-alpine

WORKDIR /app

# Installer UNIQUEMENT libpq et curl
RUN apk add --no-cache libpq curl

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

COPY --from=builder /root/.local /root/.local
COPY . .

# ✅ CORRECTION: Utiliser main.py au lieu de ENV.py
RUN echo "🔍 Vérification: main.py présent?" && \
    ls -la main.py && \
    echo "✅ main.py trouvé, utilisation comme point d'entrée"

# ✅ Utiliser main:app (l'application FastAPI dans main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000