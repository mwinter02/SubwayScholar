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
echo "Next step: open .env and set your API key:"
echo "OPENAI_API_KEY=your_openai_api_key_here"
echo
echo "After that, run:"
echo "bash run.sh"
echo "or"
echo "python main.py"
echo "use --help for more options such as voice model and background video selection."
