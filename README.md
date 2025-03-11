# AI Podcast Service README

## Overview
This repository hosts a FastAPI-based service that generates AI podcasts using OpenAI’s API. It optionally converts text to speech (TTS) via edge-tts or gTTS. It also handles usage limits and environment-based configurations (e.g., `APP_ENV`).

## Features
- **FastAPI**: Provides RESTful endpoints, including `/generate` for podcast creation.
- **OpenAI Integration**: Calls the OpenAI API to generate the podcast text.
- **TTS**: Converts generated text into speech. Defaults to edge-tts if installed, otherwise falls back to gTTS.
- **Docker Support**: Includes Dockerfiles and docker-compose configurations for development and production.
- **Usage Limit**: Enforced in production if no valid API key is provided (or by front-end logic).

## Prerequisites
- [Python 3.9+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/) or [Poetry](https://python-poetry.org/) (or your preferred dependency manager)
- Valid [OpenAI API Key](https://platform.openai.com/)

## Installation

1. **Clone the repository** (or copy the files to your server).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set environment variables** (in `.env` or otherwise):
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `APP_ENV`: `development` or `production`.
   - (Optional) `TTS_ENGINE`: If you want to specify which TTS engine to use, e.g., `edge-tts`.
4. **Run the server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   This starts the FastAPI service at [http://localhost:8000](http://localhost:8000).

## Endpoints

1. **POST /generate**
   - **Request Body**: `{ "topic": "string", "tts": bool, "user_api_key": "string (optional)" }`
   - **Response**: JSON with generated `text`, `audio_file` (URL if TTS is enabled), and optionally `timestamps` (array of time markers).
   - In production, if no valid API key is provided (and you choose to enforce it), usage might be restricted.

2. **POST /validate_api** (optional)
   - **Request Body**: `{ "user_api_key": "string" }`
   - **Response**: `{ "valid": bool, "error": string (if any) }`
   - Checks if the provided OpenAI API key is valid by making a minimal API call.

## Docker

- **Development**: Use `docker-compose.yml` (or `docker-compose.dev.yml`) to build and run. Example:
  ```bash
  docker-compose up -d --build
  ```
- **Production**: Use `docker-compose.prod.yml` or your own CI/CD pipeline to deploy in a production environment.

## Usage

1. **Send a POST request** to `/generate` with the desired topic.
2. **Receive** a JSON response containing the generated podcast text, optional audio URL, and timestamps for text synchronization.
3. **Access the audio** file at the provided URL (FastAPI static file mount).

## Notes on Environment

- **APP_ENV=development**: Typically no usage limit enforced.  
- **APP_ENV=production**: By default, usage might be limited to 3 times unless the user provides a valid API key (depending on your chosen logic).

## Contributing
- Fork the repo and create a pull request for improvements.
- Report issues via the issue tracker.

---

**Feel free to adapt these README files** to match your exact project structure and deployment methods.
