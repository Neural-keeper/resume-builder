FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl --proto '=https' --tlsv1.2 -fsSL https://typst.app/install.sh | sh \
    && ln -s /root/.local/bin/typst /usr/local/bin/typst \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "backend.src.api:app", "--host", "0.0.0.0", "--port", "8000"]