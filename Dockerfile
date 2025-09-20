FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry and uv
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && pip install uv
ENV PATH="/root/.local/bin:$PATH"

# Install poetry export plugin
RUN poetry self add poetry-plugin-export

# Copy the entire application first
COPY . .


# Install dependencies using poetry and uv
RUN poetry lock \
    && poetry export -f requirements.txt --output requirements.txt \
    && uv pip install --system -r requirements.txt --no-deps




# Expose the necessary port
EXPOSE 8081

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8081 ${EXTRA_UVICORN_ARGS}"]