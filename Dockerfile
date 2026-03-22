# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout and stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (optional, but good for psycopg2 and other packages)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install daphne==4.1.2 channels==4.1.0

# Copy the rest of the project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application locally
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
