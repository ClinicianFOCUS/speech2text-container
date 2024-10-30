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

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
import argparse
import secrets

# Initialize the HTTP Bearer scheme for token authentication
bearer_scheme = HTTPBearer()


def parse_arguments():
    """
    Parses and returns configuration arguments for the application from environment variables.

    :return: A dictionary containing the parsed configuration values with keys:
             - ``host``: The hostname or IP address.
             - ``port``: The port number.
             - ``whispermodel``: The name of the Whisper model.
    :rtype: dict

    **Environment Variables:**

    - ``WHISPER_HOST``: The hostname or IP address on which the application should listen. Default: ``"0.0.0.0"``.
    - ``WHISPER_PORT``: The port number on which the application should listen. Default: ``2224``.
    - ``WHISPER_MODEL``: The name of the Whisper model to be used. Default: ``"medium"``.
    """

    # Define default values from environment variables
    # Retrieve the host from the environment, defaulting to "0.0.0.0"
    host = os.getenv("WHISPER_HOST", "127.0.0.1")
    # Retrieve the port from the environment, defaulting to 2224, and convert to integer
    port = int(os.getenv("WHISPER_PORT", 2224))
    # Retrieve the model name from the environment, defaulting to "medium"
    whispermodel = os.getenv("WHISPER_MODEL", "medium")
    # Use gpu env
    use_gpu = os.getenv("USE_GPU", "False")

    # Return the parsed configuration as a dictionary
    return {"host": host, "port": port, "whispermodel": whispermodel, "use_gpu": use_gpu}


def generate_api_key():
    """
    Generates a secure API key.

    This function uses the `secrets` module to generate a secure, URL-safe
    API key. The key is 32 characters long.

    :return: A securely generated API key.
    :rtype: str

    **Example:**

    .. code-block:: python

        >>> api_key = generate_api_key()
        >>> print(api_key)
        'aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890'
    """

    return secrets.token_urlsafe(32)


def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Retrieves and validates the API key from the request headers.

    This function retrieves the API key from the request headers using the
    `HTTPBearer` scheme. It checks if the provided token matches the one stored
    in the environment variable ``SESSION_API_KEY``. If the token is invalid or
    missing, it raises an HTTPException with a 401 status code.

    :param credentials: The credentials extracted from the request headers.
    :type credentials: HTTPAuthorizationCredentials

    :return: The validated API key.
    :rtype: str

    :raises HTTPException:
        - 401: If the provided token is invalid or missing.

    **Example:**

    .. code-block:: python

        >>> api_key = get_api_key(credentials)
        >>> print(api_key)
        'aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890'
    """

    token = credentials.credentials
    if token == os.getenv('SESSION_API_KEY'):
        return token
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing Bearer Token",
    )


def check_api_key():
    """
    Checks and retrieves the API key from the environment variables.

    This function checks if the ``SESSION_API_KEY`` environment variable is set.
    If not, it generates a new API key and sets it in the environment variables.

    :return: The API key stored in the environment variables.
    :rtype: str

    **Example:**

    .. code-block:: python

        >>> api_key = check_api_key()
        >>> print(api_key)
        'aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890'
    """
    api_key = os.getenv('SESSION_API_KEY')

    if not api_key:
        # If not found, generate a new one and every session
        api_key = generate_api_key()
        os.environ['SESSION_API_KEY'] = api_key

    return api_key


def get_ip_from_headers(request: Request):
    """
    Extracts the client's IP address from the request headers.

    If the ``X-Forwarded-For`` header is not present, it falls back to using
    the direct client IP address from the request.

    :param request: The request object containing the headers and client info.
    :type request: Request

    :return: The client's IP address, either from the ``X-Forwarded-For`` header
             or from ``request.client.host``.
    :rtype: str

    **Example:**

    .. code-block:: python

        >>> ip = get_ip_from_headers(request)
        >>> print(ip)
        '192.168.1.1'
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.client.host
