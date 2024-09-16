# syntax=docker/dockerfile:1.2
FROM python:latest
#docker configuration here# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8080 for the API
EXPOSE 8080

# Define environment variable for the host
ENV HOST 0.0.0.0

# Command to run the application
CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8080"]