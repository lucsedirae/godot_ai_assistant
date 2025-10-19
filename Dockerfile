FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/data /app/data/lore /app/godot_docs /app/templates /app/static

# Copy application code
COPY . .

# Expose port for web interface
EXPOSE 5000

# Run web server by default
CMD ["python", "src/web_app.py"]