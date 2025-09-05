# Multi-stage Docker build for JIRA MCP Server using uv
FROM ghcr.io/astral-sh/uv:python3.9-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv venv /opt/venv && \
    uv pip install --frozen -e .

# Production stage
FROM python:3.9-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY src/ src/

# Set up path to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import jira_mcp_server; print('OK')" || exit 1

# Expose port (if running as server)
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "-m", "jira_mcp_server.cli"]
