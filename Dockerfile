FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and Microsoft ODBC drivers
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
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
EXPOSE 8088

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8088 ${EXTRA_UVICORN_ARGS}"]