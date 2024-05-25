# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for matplotlib and other potential dependencies
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    pkg-config \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Initialize database and start the application with Gunicorn
CMD ["sh", "-c", "python -c 'from app import db; db.create_all()' && gunicorn -w 4 -b :5000 app:app"]
