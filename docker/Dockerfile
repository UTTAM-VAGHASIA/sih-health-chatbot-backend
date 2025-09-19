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
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
# Change host to 127.0.0.1 from 0.0.0.0 when running locally and not from docker container
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
