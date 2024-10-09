.. test documentation master file, created by
   sphinx-quickstart on Mon Oct  7 12:56:16 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================
Unburdening Primary Healthcare
============================

.. role:: python(code)
   :language: python

Welcome to the **Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform** documentation. This project is a collaboration as part of the ClinicianFOCUS initiative with Conestoga College and Dr. Braedon Hendy. Below you'll find documentation for the core modules, API endpoints, and utilities used in this project. Below are the pages contents:




.. contents::
   :depth: 2
   :local:

Installation
============

To install and run the **speech2text-container** project with the latest changes, follow these instructions:

Prerequisites
-------------

- **Docker** and **Docker Compose** must be installed on your system.
- **Nvidia Docker runtime** must be installed. (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- **Nvidia CUDA Toolkit** must be installed. (https://developer.nvidia.com/cuda-downloads)

Installation Steps
------------------

1. **Clone the Repository**:
   
   First, clone the project repository by running the following command:

   .. code-block:: bash

      git clone https://github.com/ClinicianFOCUS/speech2text-container.git

Usage
=====

To deploy and run the speech transcription service using Docker Compose, follow the steps below.

1. **Build and run the services using Docker Compose**:

   The project includes a `docker-compose.yml` file to simplify the setup of the speech transcription service. This file defines two services: 
   - `speech-container` for the Whisper speech transcription model.
   - `caddy` for handling reverse proxy duties.

2. **Prerequisites**:
   - Install Docker and Docker Compose on your system.
   - Ensure that the necessary ports (default: 2224) are available on your machine.

3. **Starting the Services**:

   Run the following command to build and start the containers:
   
   .. code-block:: bash

      docker-compose up --build

   This will:
   - Build the `speech-container` using the provided `Dockerfile` and start it with the specified `WHISPER_MODEL`, `WHISPER_PORT`, and `WHISPER_HOST`.
   - Build and run the `caddy` container as a reverse proxy.

4. **Service Configuration**:

   The following environment variables can be customized to control the behavior of the `speech-container` service:

   - `WHISPER_MODEL`: The Whisper model to use (default: `medium`).
   - `WHISPER_PORT`: The port to expose the service (default: `2224`).
   - `WHISPER_HOST`: The host to bind the service (default: `0.0.0.0`).
   - `UVICORN_WORKERS`: Number of Uvicorn workers (default: `1`).

   **Example**:

   .. code-block:: bash

      WHISPER_MODEL=large WHISPER_PORT=8080 WHISPER_HOST=127.0.0.1 docker-compose up --build

   This will start the transcription service with the `large` Whisper model on port `8080`, accessible only from `127.0.0.1`.

5. **Stopping the Services**:

   To stop the services, use the following command:

   .. code-block:: bash

      docker-compose down

   This will stop and remove the containers but will retain the built images.

API Reference
=============

Below are the available API endpoints for interacting with the Whisper Server.

.. _whisperaudio:

Whisper Audio Endpoint
----------------------

**URL**: ``/whisperaudio``

**Method**: ``POST``

**Description**:
This endpoint accepts an audio file (MP3 or WAV) and transcribes it using the Whisper model. Ensure that an API key is provided via the Authorization Bearer header.

**Parameters**:
  - **file** (required): The audio file (MP3 or WAV).
  - **api_key** (required): A valid API key for accessing the endpoint.

**Response**:
  - 200: Transcription text in a JSON format.
  - 400: Invalid file type.
  - 401: Unauthorized.
  - 413: Request entity too large.
  - 419: Rate limit exceeded.
  - 500: Server error.

**Example**:

.. code-block:: bash

   curl -X POST "http://localhost:2224/whisperaudio" \
        -H "Authorization: Bearer <api_key>" \
        -F "file=@/path/to/audiofile.wav"

Response:

.. code-block:: json

   {
       "text": "Transcribed text here"
   }

Python Modules
==============

Below are the core Python modules used in this project.

.. toctree::
   :maxdepth: 2

   source/modules

.. Contributing
.. ============

.. We welcome contributions! Please refer to the ``CONTRIBUTING.md`` file for guidelines on how to contribute to this project.

.. Changelog
.. =========

.. All notable changes to this project will be documented in the ``CHANGELOG.md`` file.
