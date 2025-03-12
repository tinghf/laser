# Use Rocky Linux as base
# FROM rockylinux:9

# Use the official Python image as the base image
FROM python:3.12-slim

# Install Python 3.12 and dependencies
# RUN python3 -m ensurepip && \
#    python3 -m pip install --upgrade pip

# Set the working directory inside the container
WORKDIR /app

# install system dependencies
# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY cluster/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY laser.py .
COPY params.json .

# Copy the Optuna script and the objective function module into the container
COPY cluster/test_ray_remote_workers.py .
COPY cluster/model.py .


# Run the script when the container starts
# CMD ["python3", "laser.py"]
