# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for archives (MCP Tools)
RUN mkdir -p archives/audit_logs

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
