# KPS-Hub Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY db.py seed.py admin.py server.py .

# Initialize database
RUN python -c "from db import HubRepository; from seed import seed_database; repo = HubRepository(); seed_database(repo)"

EXPOSE 8000

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
