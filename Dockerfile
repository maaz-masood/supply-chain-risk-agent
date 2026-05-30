FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY . .

# Install dependencies
RUN uv pip install --system fastapi uvicorn sqlalchemy \
    psycopg2-binary pandas python-dotenv \
    langgraph langchain langchain-openai httpx \
    google-auth google-auth-oauthlib \
    google-auth-httplib2 google-api-python-client

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]