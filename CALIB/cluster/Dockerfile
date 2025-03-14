# Use Rocky Linux as base
FROM rockylinux:9

# Use the official Python image as the base image
# FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN dnf update -y && \
    dnf install -y epel-release && \
    dnf install -y \
    python3 \
    python3-devel \
    mariadb-connector-c-devel \
    gcc \
    gcc-c++ \
    make \
    wget \
    screen \
    procps \
    vim \
    git \
    && dnf clean all

# Upgrade pip
RUN python3 -m ensurepip && \
    python3 -m pip install --upgrade pip

   
# install system dependencies
# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     default-libmysqlclient-dev \
#     build-essential \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY cluster/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY laser.py .
COPY params.json .
COPY run.py .
COPY objective.py .
COPY impatient.py .

# Copy the Optuna script and the objective function module into the container
COPY cluster/test_ray_remote_workers.py .
COPY cluster/model.py .
COPY cluster/check_study.sh .


# Run the script when the container starts
# CMD ["python3", "laser.py"]
