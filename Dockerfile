# Use a slim python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else from your current directory
COPY . .

# Run the command exactly as you run it on your system
CMD ["python", "rank.py", "--candidates", "./candidates.jsonl", "--out", "./submission.csv"]