# FreeScribe Speech-to-Text Server

This software is released under the AGPL-3.0 license  
Copyright (c) 2023-2024 Braedon Hendy

Part of the ClinicianFOCUS initiative, a collaboration with Conestoga College Institute of Applied Learning and Technology's CNERG+ applied research project.

## Overview

FreeScribe is an open-source speech-to-text server that utilizes OpenAI's Whisper model for audio transcription. It provides a robust API endpoint for converting audio files to text, with support for various audio formats including MP3, WAV, and WebM.

## Features

- Fast audio transcription using Whisper AI
- Support for multiple audio formats (MP3, WAV, WebM)
- Rate limiting protection
- API key authentication
- GPU support for faster processing
- Docker containerization
- Reverse proxy setup with Caddy

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (optional, for GPU acceleration)
- NVIDIA Container Toolkit (if using GPU)

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
WHISPER_MODEL=medium    # Whisper model size (tiny, base, small, medium, large) (Default: medium)
WHISPER_PORT=2224      # Port for the service (Default: 2224)
WHISPER_HOST=0.0.0.0   # Host address (Default: 0.0.0.0)
UVICORN_WORKERS=1      # Number of Uvicorn workers (Default: 1)
```

## Deployment Options

### CPU-Only Deployment

```bash
docker-compose -f docker-compose.cpu.yml up --build
```

### GPU-Enabled Deployment

```bash
docker-compose up --build
```

## Container Structure

The application consists of two main containers:

1. **speech-container**

   - Runs the FastAPI application
   - Handles audio transcription
   - Configurable for CPU or GPU usage

2. **caddy**
   - Reverse proxy
   - Handles HTTPS termination
   - Manages incoming traffic

## API Usage

### Endpoint: POST /health

API to check if container is running.

**Response:**

```json
{
  "status": "ok"
}
```

### Endpoint: POST /whisperaudio

Transcribe an audio file to text.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Authorization: Bearer <api_key>
- Body: audio file (MP3, WAV, or WebM)

**Response:**

```json
{
  "text": "Transcribed text from the audio file."
}
```

## Rate Limiting

- Default rate limit: 1 request per second
- Rate limit errors return 429 status code

## License

This project is licensed under the AGPL-3.0 License - see the LICENSE file for details.
