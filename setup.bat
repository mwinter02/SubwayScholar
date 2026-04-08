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
echo Next step: open .env and set your API key:
echo OPENAI_API_KEY=your_openai_api_key_here
echo.
echo After that, run:
echo run.bat
echo or
echo python main.py
echo use --help for more options such as voice model and background video selection.


endlocal
