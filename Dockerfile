FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "python src/shopping_agent/setup_db.py && python -m streamlit run src/shopping_agent/app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]

