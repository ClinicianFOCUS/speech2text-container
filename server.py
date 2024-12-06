"""
This software is released under the AGPL-3.0 license
Copyright (c) 2023-2024 Braedon Hendy

Further updates and packaging added in 2024 through the ClinicianFOCUS initiative, 
a collaboration with Dr. Braedon Hendy and Conestoga College Institute of Applied 
Learning and Technology as part of the CNERG+ applied research project, 
Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform". 
Prof. Michael Yingbull (PI), Dr. Braedon Hendy (Partner), 
and Research Students - Software Developer Alex Simko, Pemba Sherpa (F24), and Naitik Patel.
"""

from torch._C import NoneType
from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Request
from dotenv import load_dotenv
from utils import check_api_key, get_api_key, parse_arguments, get_ip_from_headers
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from pydub import AudioSegment
import whisper
import uvicorn
import os
import tempfile
import magic
import logging
import logging
import io
import librosa

# Load environment variables from a .env file
load_dotenv()

# Ensure the directory exists
log_dir = "/tmp/FreeScribe/"
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "Server.log")),
        logging.StreamHandler(),  # Keeps logging in the console as well, if needed
    ],
)

# Setup the whispermodel var and api key var
MODEL = None
SESSION_API_KEY = None

# Configure logging to display INFO level messages
logging.basicConfig(level=logging.INFO)

# set a default rate limit of 5 requests per minute
limiter = Limiter(
    key_func=get_ip_from_headers, default_limits=["1/second"]
)  # Example: Limit to 5 requests per minute


# Create a FastAPI application instance
app = FastAPI()
app.state.limiter = limiter


# Add middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """
    This function adds middleware to an application for rate limiting HTTP requests. 
    It processes incoming requests and either forwards them for handling or returns a `429 Too Many Requests` 
    response if the rate limit is exceeded.

    Example:
    --------

    .. code-block:: python

        @app.middleware("http")
        async def rate_limit_middleware(request, call_next):
            try:
                response = await call_next(request)
                return response
            except RateLimitExceeded as e:
                logging.warning(f"Rate limit exceeded: {e}")
                return PlainTextResponse("Rate limit exceeded. Try again later.", status_code=429)

    Parameters:
    -----------
    - `request` : The incoming HTTP request.
    - `call_next` : Callable to pass the request to the next handler.

    Returns:
    --------
    - `response` : The HTTP response from the next handler in the middleware chain.
    - If the rate limit is exceeded, returns a `PlainTextResponse` with a 429 status code and a "Rate limit exceeded" message.

    Raises:
    -------
    - `RateLimitExceeded` : Raised when the request exceeds the allowed rate limit.
    """
    try:
        response = await call_next(request)
        return response
    except RateLimitExceeded as e:
        logging.warning(f"Rate limit exceeded: {e}")
        return PlainTextResponse(
            "Rate limit exceeded. Try again later.", status_code=429
        )

# Processing files to aud format and reutrning its data with temp file  name
def normalize_audio(file_content: bytes, file_type: str) -> tuple[bytes, str]:
    if file_type == "video/webm":
        audio = AudioSegment.from_file(io.BytesIO(file_content), format="webm")
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue(), ".wav"
    
    # Mapping of MIME types to file extensions
    mime_to_extension = {
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        # Add more mappings if needed
    }
    
    # Get the correct extension based on the file type
    extension = mime_to_extension.get(file_type, "")  # Default to empty string if not found
    return file_content, extension


# Define the endpoint for transcribing audio files
@app.post("/whisperaudio")
@limiter.limit("10/second")
async def transcribe_audio(
    request: Request, audio: UploadFile = File(...), api_key: str = Security(get_api_key)
):
    """
    Transcribes an uploaded audio file using the Whisper model.

    This endpoint accepts an audio file (MP3 or WAV) and an API key for authentication.
    It validates the file type, saves the file temporarily, transcribes it using the
    Whisper model, and returns the transcribed text.

    :param request: The request object containing headers and client information.
    :type request: fastapi.Request
    :param file: The audio file to be transcribed. Must be an MP3 or WAV file.
    :type file: fastapi.UploadFile
    :param api_key: The API key for authentication. Retrieved using the `get_api_key` function.
    :type api_key: str

    :return: JSON response containing the transcribed text.
    :rtype: dict

    :raises HTTPException:
        - 400: If the uploaded file is not an MP3 or WAV file.
        - 500: If there is an error processing the audio file.

    **Example:**

    .. code-block:: bash

        POST /whisperaudio
        Content-Type: multipart/form-data
        Authorization: Bearer <api_key>

        {
            "audio": <audio_file>
        }

    **Response:**

    .. code-block:: json

        {
            "text": "Transcribed text from the audio file."
        }
    """

    # Verify file type
    mime = magic.Magic(mime=True)
    file_content = await audio.read()
    file_type = mime.from_buffer(file_content)
    
    if file_type not in ["audio/mpeg", "audio/wav", "audio/x-wav", "video/webm"]:
        logging.warning(f"Invalid file type: {file_type}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an MP3, WAV, or WEBM file.",
        )

    try:
        normalized_content, suffix = normalize_audio(file_content, file_type)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(normalized_content)
            temp_file.write(file_content)
            temp_path = temp_file.name
                # Transcribe using temporary file
            result = MODEL.transcribe(
                temp_path,
            )
        
        return {"text": result["text"]}
    
    except Exception as e:
        logging.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if 'temp_path' in locals():
            os.remove(temp_path)


# Main entry point for running the Whisper servers


@app.on_event("startup")
async def startup_event():
    """
    Asynchronous function that runs during the application startup.

    This function performs several initialization tasks:
    1. Parses the command-line arguments to retrieve configuration settings.
    2. Loads the Whisper model using the specified model name.
    3. Checks and retrieves the API key for authentication.
    4. Prints the API key for reference.

    The function uses the global variable `MODEL` to store the loaded Whisper model.

    The function uses the global variable `SESSION_API_KEY` to store the API key.

    Returns:
    - None
    """

    # Parse command-line arguments
    args = parse_arguments()

    # Load the Whisper model using the specified model name
    global MODEL
    device = "cuda" if args["use_gpu"] is True else "cpu"

    # Check and retrieve the API key\
    global SESSION_API_KEY
    SESSION_API_KEY = check_api_key()

    MODEL = whisper.load_model(name=args["whispermodel"], device=device)

    # Print API key information and security warnings
    print("\n" + "="*50)
    print(" " * 5 + "⚠️ IMPORTANT: API Key Information ⚠️" + " " * 5)
    print("="*50)
    print("\n" + " " * 3 + f" Session API Key: {SESSION_API_KEY} " + "\n")
    print("="*50)
    print("\nNOTE:")
    print("- Do not share your API key publicly.")
    print("- Avoid committing API keys in code repositories.")
    print("- If exposed, reset and replace it immediately.\n")
    print("="*50 + "\n")
