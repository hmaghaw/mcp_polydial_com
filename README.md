apt update
apt install curl -y
curl -LsSf https://astral.sh/uv/install.sh | sh

curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g @modelcontextprotocol/inspector@0.17.0


source $HOME/.local/bin/env

uv venv --python 3.11
source .venv/bin/activate

mcp dev src/mcp_minimal/server.py

uv run --with mcp main.py