# Use Python 3.13 slim image (matches your pyproject.toml)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for uvicorn, requests, psycopg2 later)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip & install dependencies directly from pyproject.toml
# (since we are not using poetry.lock here)
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip \
    && pip install fastapi uvicorn[standard] requests python-dotenv

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"]
