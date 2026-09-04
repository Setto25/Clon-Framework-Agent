FROM python:3.13-slim

WORKDIR /aplicacion

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv==0.11.28 && uv sync --frozen --no-dev

COPY codigo_servidor ./codigo_servidor

ENV PATH="/aplicacion/.venv/bin:$PATH"
ENV PORT=8080

CMD ["sh", "-c", "uvicorn codigo_servidor.entrada_http:aplicacion --host 0.0.0.0 --port ${PORT}"]
