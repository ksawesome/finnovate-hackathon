FROM python:3.11-slim AS builder

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml environment.yml ./

# Install pip deps directly (simplified since project uses conda locally)
RUN pip install --upgrade pip && pip install streamlit pandas sqlalchemy pymongo great-expectations mlflow chromadb faiss-cpu plotly scikit-learn pydantic guardrails-ai psycopg2-binary pyarrow

COPY src ./src
COPY data/sample ./data/sample

FROM python:3.11-slim AS runtime
WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src
COPY --from=builder /app/data ./data

USER appuser
ENV STREAMLIT_SERVER_PORT=8501
EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "src/app.py"]
