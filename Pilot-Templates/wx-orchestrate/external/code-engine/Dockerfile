# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by Pillow (for image formats)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev zlib1g-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose MCP server port
EXPOSE 8085

# Set environment variables for FastMCP
ENV PYTHONUNBUFFERED=1

# Run FastMCP server
CMD ["python", "main.py"]