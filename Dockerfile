# ✅ Official Python image
FROM python:3.13-slim

# ✅ Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# ✅ Workdir
WORKDIR /app

# ✅ Install dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    bash ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ✅ Copy and install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy project
COPY . /app

# ✅ Auto-loop every 30 minutes
CMD ["bash", "-lc", "while true; do python -m src.main --symbols-file sample_symbols.txt --once; sleep 1800; done"]
