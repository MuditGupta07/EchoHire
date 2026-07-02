# Start with a base image that has Python and Node.js
FROM python:3.11-slim

# Install system dependencies & Node.js for building the frontend
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Setup Backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Setup Frontend
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

# 3. Finalize
WORKDIR /app
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]