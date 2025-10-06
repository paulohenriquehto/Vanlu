# VanLu Agent - Dockerfile otimizado para deploy via GitHub
FROM python:3.11-slim

# Metadata labels
LABEL maintainer="Paulo Henrique <paulohenriquehto@gmail.com>"
LABEL description="VanLu Agent - Sistema de IA com LangGraph e FastAPI"
LABEL version="1.0"
LABEL source="https://github.com/paulohenriquehto/Vanlu.git"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r vanlu && useradd -r -g vanlu -d /app -s /bin/bash vanlu

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p logs \
    && chown -R vanlu:vanlu /app \
    && chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER vanlu

# Expose port
EXPOSE 2024

# Health check using the correct endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:2024/health || exit 1

# Run the application
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]