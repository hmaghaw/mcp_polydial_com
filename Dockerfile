# ----------------------------------------------------------
# Base image for MCP Minimal Server
# Installs system tools (Python, Node.js, npm, curl)
# ----------------------------------------------------------
FROM debian:latest
WORKDIR /app
COPY ./app /app
# Install OS-level dependencies
RUN  apt update
RUN  apt install curl -y
RUN  curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"


RUN  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN  apt install -y nodejs
RUN  npm install -g @modelcontextprotocol/inspector@0.15.0

RUN . $HOME/.local/bin/env

RUN uv venv --python 3.11 && \
 . .venv/bin/activate && \
 uv sync