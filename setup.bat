@echo off
setlocal

if not exist venv (
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
  copy .env.example .env >nul
  echo Created .env from .env.example
) else (
  echo .env already exists. Keeping existing file.
)

echo.
echo Setup complete.
echo Next step:
echo 1) Run manual mode (default, no API key required):
echo    python main.py ^<pdf_path^>
echo.
echo 2) Or run API mode (requires OPENAI_API_KEY in .env):
echo    python main.py ^<pdf_path^> --use-openai-api
echo.
echo Use --help for options such as voice model and background video selection.


endlocal
