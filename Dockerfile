FROM python:3.11-slim

# Install system dependencies including libreoffice and poppler-utils
RUN apt-get update && apt-get install -y \
    curl \
    libreoffice \
    poppler-utils \
    ghostscript \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Ensure entrypoint script is properly copied & executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose the port Django runs on
EXPOSE 8000

# Default command will be specified in docker-compose.yml
