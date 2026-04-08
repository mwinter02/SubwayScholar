# SubwayScholar

Convert a research paper PDF into a short narrated MP4 video that retains your attention.

Pipeline overview:
1. Extract text and images from PDF (PyMuPDF)
2. Generate a short narration script (OpenAI API)
3. Convert script to speech (local Piper TTS)
4. Compose final video (MoviePy)

## Project Summary

This project was created as an exercise in agentic AI development.

I used ChatGPT to brainstorm the idea: take a research paper PDF and turn it
into short-form content with Subway Surfers gameplay in the background.
ChatGPT was then used to define the structure, gather requirements, and generate
prompts for GPT-Codex.

Those prompts were given to Codex, which implemented the project end-to-end
with minimal intervention. I did not directly write code during the build.

Key practices that enabled immediate success:
- Keeping the system modular
- Specifying clear API contracts
- Defining project structure up front
- Managing focused context windows

## Requirements

- Python 3.10+
- `pip`
- Internet access for first-time model/dependency download
- OpenAI API key (`OPENAI_API_KEY`) for script generation

Installed Python dependencies are managed in `requirements.txt`.


## Setup

Use the setup scripts to create venv, install dependencies, and create `.env` from `.env.example`.

### Mac/Linux

```bash
bash setup.sh
```

### Windows

```bat
setup.bat
```

After setup, open `.env` and set:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run

### One-command run (recommended)

Mac/Linux:
```bash
bash run.sh
```

Windows:
```bat
run.bat
```

### Run directly with Python

Mac/Linux:
```bash
source venv/bin/activate
python main.py
```

Windows (CMD):
```bat
call venv\Scripts\activate.bat
python main.py
```

## Optional Main Arguments

`main.py` supports optional runtime overrides:

- `--voice-model` (default: `en_US-lessac-medium.onnx`)
- `--background-video` (default: `assets/background.mp4`)

Example:

```bash
python main.py --voice-model en_US-lessac-medium --background-video assets/background.mp4
```

Notes:
- Default Piper model files are auto-downloaded to `models/` if missing.
- Custom voice models should exist in `models/` as:
  - `<model>.onnx`
  - `<model>.onnx.json`

## Tests

Run module tests with `test.py`:

```bash
python test.py -h
```

Examples:

```bash
python test.py -pdf assets/example.pdf
python test.py -llm tests/pdf/extracted_text.txt
python test.py -tts tests/llm/generated_script.txt
python test.py -video outputs/audio/output.wav tests/video/test.mp4 outputs/images/image_1.png
```

Test outputs are written to:
- `tests/pdf/`
- `tests/llm/`
- `tests/tts/`
- `tests/video/`

## Project Structure

```text
project_root/
│
├── main.py
├── test.py
├── requirements.txt
├── README.md
├── setup.sh
├── setup.bat
├── run.sh
├── run.bat
├── .env.example
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
├── models/                 # Piper voice models (auto-downloaded)
├── outputs/
│   ├── audio/
│   ├── images/
│   └── video/
│
└── tests/
    ├── test_pdf_module.py
    ├── test_llm_module.py
    ├── test_tts_module.py
    ├── test_video_module.py
    ├── pdf/
    ├── llm/
    ├── tts/
    └── video/
```

