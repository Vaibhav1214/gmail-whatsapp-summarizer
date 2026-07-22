# Use official slim Python runtime as base image
FROM python:3.11-slim

# Prevent Python from writing pyc files to disk and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy dependency specifications
COPY requirement/requirements.txt /app/requirement/

# Install dependencies
RUN pip install --no-cache-dir -r requirement/requirements.txt

# Copy application files
COPY gmail_tools.py whatsapp_tools.py config.py logger.py main.py /app/

# Define default execution command (binds dynamically to Cloud Run $PORT)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
