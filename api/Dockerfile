FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements (optional) and install
COPY requirements-dev.txt requirements.txt* ./
RUN if [ -f requirements-dev.txt ]; then \
      pip install --no-cache-dir -r requirements-dev.txt; \
    elif [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      echo "No requirements file found, skipping"; \
    fi

# Source code will be mounted as a volume in docker-compose for hot-reload
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]


