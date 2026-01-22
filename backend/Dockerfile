# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2 and other tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --default-timeout=1000 -r requirements.txt

# Copy config files (alembic.ini needs to be in root relative to backend execution usually, or explicitly pointed to)
# We copy it to /app/alembic.ini
COPY alembic.ini .

# Copy the backend code
COPY backend/ ./backend/

# Copy entrypoint script and make it executable
COPY backend/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && sed -i 's/\r$//' /usr/local/bin/entrypoint.sh

# Expose port
EXPOSE 8003

# Run the application via entrypoint
CMD ["/usr/local/bin/entrypoint.sh"]
