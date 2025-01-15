# Use the official Python image
FROM python:3.10-slim

# Create a group with GID 1000 and a user with UID 1000
RUN addgroup --gid 1000 appgroup && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" appuser

# Update the system and install necessary tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i cuda-keyring_1.1-1_all.deb \
    && apt-get update \
    && apt-get -y install cudnn-cuda-12

# Set the working directory
WORKDIR /app

#setup dir we will need and set non root user perms
RUN mkdir -p /.cache && chown -R 1000:1000 /.cache

# Copy the Speech2text server code into the container
COPY ./requirements.txt .

#Upgrade pip
RUN python -m pip install --upgrade pip

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

#Pip Install the required packages for the GPU
RUN pip install torch --index-url https://download.pytorch.org/whl/cu121

# Install the required packages for python magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && apt-get clean


# Install ffmpeg required for whisper transcription
RUN apt-get install ffmpeg -y

# copy the rest of the directory into the container
COPY ./server.py .
COPY ./utils.py .

# Expose the port the app runs on
EXPOSE 2224