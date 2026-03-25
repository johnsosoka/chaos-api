# Chaos API

[![CI](https://github.com/johnsosoka/chaos-api/actions/workflows/ci.yml/badge.svg)](https://github.com/johnsosoka/chaos-api/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A FastAPI application that accepts **any endpoint and any HTTP method**, then uses an LLM (via LangChain + OpenAI) to generate a realistic fake REST API response. The model infers what API would logically exist at the requested path and returns plausible data — not placeholder text.

## Concept

Send a request to `/users/42` and get back a realistic JSON user object. Hit `/weather/london` with `Accept: application/xml` and receive a well-formed XML weather response. The API pretends to be whatever service would plausibly live at that URL.

## Features

- **Universal Endpoint**: Accepts any path and HTTP method
- **Content Negotiation**: Supports JSON, XML, HTML, and plain text responses
- **Production Ready**: Rate limiting, request logging, health checks, and metrics
- **Dockerized**: Ready-to-use Docker images for easy deployment
- **Well Tested**: Comprehensive test suite with 80%+ coverage
- **Type Safe**: Fully typed with mypy

## Quick Start

### Using Docker

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key johnsosoka/chaos-api
```

### Using Docker Compose

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

docker-compose up chaos-api
```

### Local Development

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the server
poetry run uvicorn src.chaos_api.main:app --reload --port 8000
```

## Usage Examples

### JSON API (default)

```bash
# List users
curl http://localhost:8000/users

# Get a specific user
curl http://localhost:8000/users/42

# Create an order
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "abc123", "quantity": 2}'
```

### XML Response

```bash
curl http://localhost:8000/weather/london \
  -H "Accept: application/xml"
```

### HTML Response

```bash
curl http://localhost:8000/products \
  -H "Accept: text/html"
```

### Plain Text

```bash
curl http://localhost:8000/health \
  -H "Accept: text/plain"
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

## Supported Response Types

| MIME Type          | Description              |
|--------------------|--------------------------|
| `application/json` | JSON (default)           |
| `application/xml`  | XML                      |
| `text/html`        | HTML page or fragment    |
| `text/plain`       | Plain text               |

The response type is determined by the `Accept` header. Defaults to `application/json` when no `Accept` header is present or no supported type matches.

## Architecture

```mermaid
flowchart TD
    Client[Client Request] --> Middleware[Middleware Layer]
    Middleware --> Router[FastAPI Router]
    Router --> Handler[Request Handler]
    Handler --> MIME[MIME Handler]
    Handler --> Prompt[Prompt Builder]
    Prompt --> LLM[LLM Client<br/>LangChain + OpenAI]
    LLM --> Handler
    Handler --> Response[Response]

    subgraph Middleware
        RequestID[Request ID]
        RateLimit[Rate Limiting]
        Logging[Request Logging]
    end

    subgraph Routes
        Health[/health]
        Metrics[/metrics]
        CatchAll[/{path}]
    end
```

### Component Overview

- **Request Handler**: Extracts request context (method, path, headers, body)
- **MIME Handler**: Parses Accept headers and formats request bodies
- **Prompt Builder**: Constructs LLM prompts from request context
- **LLM Client**: Wraps LangChain/OpenAI for response generation
- **Middleware**: Request ID tracing, rate limiting, and logging

## Configuration

All configuration is done via environment variables:

| Variable               | Default         | Description                          |
|------------------------|-----------------|--------------------------------------|
| `OPENAI_API_KEY`       | *(required)*    | Your OpenAI API key                  |
| `MODEL_NAME`           | `gpt-4o-mini`   | OpenAI model to use                  |
| `LOG_LEVEL`            | `INFO`          | Logging level (DEBUG, INFO, etc.)    |
| `RATE_LIMIT_REQUESTS`  | `100`           | Max requests per window per IP       |
| `RATE_LIMIT_WINDOW`    | `60`            | Rate limit window in seconds         |
| `DEBUG`                | `false`         | Enable debug mode                    |

## Development

### Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ --cov=src/chaos_api --cov-report=term-missing
```

### Code Quality

```bash
# Linting
poetry run ruff check src/ tests/
poetry run ruff check --fix src/ tests/

# Formatting
poetry run ruff format src/ tests/

# Type checking
poetry run mypy src/
```

### Using the Example Client

```bash
# Run all examples
python examples/client.py

# Run specific example
python examples/client.py --example json

# Use with custom URL
python examples/client.py --url http://api.example.com
```

## Project Structure

```
chaos-api/
├── src/chaos_api/          # Main application code
│   ├── main.py             # FastAPI application
│   ├── config.py           # Pydantic settings
│   ├── llm_client.py       # LangChain LLM wrapper
│   ├── mime_handlers.py    # MIME type detection
│   ├── prompt_builder.py   # LLM prompt construction
│   ├── middleware.py       # Request middleware
│   └── routes.py           # Health/metrics endpoints
├── tests/                  # Test suite
├── examples/               # Example client scripts
├── .github/workflows/      # CI/CD configuration
├── Dockerfile              # Production Docker image
├── docker-compose.yml      # Docker Compose configuration
└── pyproject.toml          # Poetry dependencies
```

## API Endpoints

### Catch-All Endpoint

- **URL**: `/{path:path}`
- **Methods**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS, TRACE
- **Description**: Generates fake API responses for any path

### Health Check

- **URL**: `/health`
- **Method**: GET
- **Response**: `{"status": "healthy", "version": "0.1.0", "uptime_seconds": 123}`

### Metrics

- **URL**: `/metrics`
- **Method**: GET
- **Response**: `{"uptime_seconds": 123, "total_requests": 42, ...}`

## Deployment

### Docker

```bash
# Build image
docker build -t chaos-api .

# Run container
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key chaos-api
```

### Docker Compose

```bash
# Production
docker-compose up -d chaos-api

# Development with hot reload
docker-compose --profile dev up -d chaos-api-dev
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- LLM integration via [LangChain](https://python.langchain.com/)
- Powered by [OpenAI](https://openai.com/)
