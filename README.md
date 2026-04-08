# Research Paper to Narrated Video

This project scaffolds a modular Python pipeline to convert a research paper (PDF) into a short narrated video (MP4).


## Sources

- Subway surfers stock footage - [
Subway Surfers (2024) - Gameplay [4K 9x16] No Copyright](https://www.youtube.com/watch?v=QPW3XwBoQlw)

- TTS model: Piper


## Project Structure

```text
project_root/
│
├── main.py
├── requirements.txt
├── README.md
├── run.sh
├── run.bat
│
├── modules/
│   ├── pdf_module.py
│   ├── llm_module.py
│   ├── tts_module.py
│   └── video_module.py
│
├── assets/
│   └── background.mp4
│
├── outputs/
│   ├── audio/
│   ├── images/
│   └── video/
│
└── temp/
```

## Setup

Create a local `.env` file for your OpenAI API key:

```bash
cp .env.example .env
```

Then set your key in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

You can also set your OpenAI API key as an environment variable before running:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

## Mac/Linux

### Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### One-Command Run

```bash
bash run.sh
```

## Windows

### Manual Setup

```bat
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

### One-Command Run

```bat
run.bat
```

## Notes

- Current implementation is scaffold-only with TODOs.
- Module interfaces are in place for future implementation.
