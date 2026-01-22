# API Documentation

PromptShield provides a comprehensive API documentation generated automatically by FastAPI using the OpenAPI standard.

## Accessing Documentation

When the backend server is running (locally or via Docker), you can access the interactive documentation at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Key Endpoints

### Execution
- `POST /api/v1/execute`: Main entry point. Compresses prompt, executes via LLM (if configured), and logs metrics.
- `POST /api/v1/replay/{log_id}`: Re-run a previous execution with the same parameters.

### Compression & Analysis
- `POST /api/v1/compress`: Convert Raw Text -> CSC (Compressed Semantic Code).
- `POST /api/v1/analyze`: Get detailed breakdown of the compression (Tokens, Entities, etc.).

### Analytics
- `GET /api/v1/stats/summary`: Aggregate metrics (Total tokens saved, etc.).
- `GET /api/v1/stats/history`: Recent activity logs.

### System
- `GET /api/v1/health`: Service health check.

## Authentication
Currently, the API is open for internal use. Future versions will implement API Key authentication via `Authorization` header.
