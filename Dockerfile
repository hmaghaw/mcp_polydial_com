# ----------------------------------------------------------
# Base image for MCP Minimal Server
# Installs system tools (Python, Node.js, npm, curl)
# ----------------------------------------------------------
FROM debian:latest
WORKDIR /app

# Install OS-level dependencies
RUN  apt update
RUN  apt install curl -y
RUN  curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"


# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @modelcontextprotocol/inspector@0.15.0

COPY ./app /app
RUN uv venv --python 3.11 && \
 . .venv/bin/activate && \
 uv sync