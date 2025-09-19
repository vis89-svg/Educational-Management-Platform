# Use official Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Prevents Python from writing .pyc files & enables stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run gunicorn (production) instead of Django dev server
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
