# speech2text-container

Containerized solution for AI speech-to-text that can run locally

# Prerequisites

Docker and Docker-compose installed on your system.

# Build and run

1. Install

```bash
git clone https://github.com/ClinicianFOCUS/speech2text-container.git
```

2. Navigate into the directory

```bash
cd speech2text-container
```

- **Recommended Step:** Set a API key in the .env file. this will be the key used to access the API. If this step is skipped the container wil generate a random key for you upon each start.

3. Build and run the docker images using docker-compose

```bash
docker-compose up -d --build
```

# Usage

Send a Request: Send audio data to the exposed endpoint on http://localhost:2224/whisperaudio

The following environment variables can be customized to control the behavior of the `speech-container` service:

- `WHISPER_MODEL`: The Whisper model to use (default: `medium`).
- `WHISPER_PORT`: The port to expose the service (default: `2224`).
- `WHISPER_HOST`: The host to bind the service (default: `0.0.0.0`).
- `UVICORN_WORKERS`: Number of Uvicorn workers (default: `1`).
- `USE_GPU`: Whether to use the GPU for inference. Default: `"True"`.

**Windows Example**

```Bash
$env:WHISPER_MODEL="large"; $env:WHISPER_PORT="2224"; $env:WHISPER_HOST="127.0.0.1"; docker-compose up -d --build
```

**Linux Example**:

NOTE: Not tested in a linux environment

```bash
WHISPER_MODEL=large WHISPER_PORT=2224 WHISPER_HOST=127.0.0.1 docker-compose up -d --build

```

This will start the transcription service with the `large` Whisper model on port `2224`, accessible only from `127.0.0.1`.

# Authentication

On server start up you will receive a api key in the console. This key changes on each start up of the software.

You can set your own API key in the .env. This will be your authentication key when launched in the container.

# Example request

```bash
   curl -X POST "http://localhost:2224/whisperaudio" \
        -H "Authorization: Bearer <api_key>" \
        -F "file=@/path/to/audiofile.wav"
```

# Example response

```json
{
  "text": "Transcribed text here"
}
```

# License

This project is licensed under the AGPL-3.0 License. See the LICENSE file for details.
