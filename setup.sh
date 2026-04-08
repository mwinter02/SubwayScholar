#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists. Keeping existing file."
fi

echo
echo "Setup complete."
echo "Next step:"
echo "1) Run manual mode (default, no API key required):"
echo "   python main.py <pdf_path>"
echo
echo "2) Or run API mode (requires OPENAI_API_KEY in .env):"
echo "   python main.py <pdf_path> --use-openai-api"
echo
echo "Use --help for options such as voice model and background video selection."
