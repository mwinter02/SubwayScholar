# SubwayScholar

Convert a research paper PDF into a short narrated MP4 video with gameplay in the background.

## Examples
Using the [ReSTIR GI](https://research.nvidia.com/publication/2021-06_restir-gi-path-resampling-real-time-path-tracing) paper, here is an [example video output](https://drive.google.com/file/d/1EgaTgdD6D-JXlal6tSBxRBzTg8nun0Sm/view?usp=sharing)

## Project Summary

This project was created as an exercise in agentic AI development.

The idea was brainstormed in ChatGPT: take a research paper PDF and transform it into short-form content with Subway Surfers-style background video. ChatGPT was used to define architecture, requirements, and implementation prompts for Codex.

Codex then implemented the project end-to-end with minimal intervention. No manual coding was needed during the build process.

Key success factors:
- Modular architecture
- Clear API contracts between modules
- Strong upfront structure
- Focused context windows for each step

End to end this project took roughly 3 hours, most of which was spent brainstorming and waiting for Codex to implement features. Due to the careful construction of the prompts, no debugging or intervention was required throughout.

## Requirements

- Python 3.10+
- `pip`
- Internet access for first-time dependency/model downloads
- Optional: OpenAI API key (`OPENAI_API_KEY`) only if using API mode

All Python dependencies are managed in `requirements.txt`.

## Setup

Use setup scripts to create a virtual environment, install dependencies, and create `.env` from `.env.example`.

### Mac/Linux

```bash
bash setup.sh
```

### Windows

```bat
setup.bat
```

If you plan to use API mode, add this to `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Running

Run directly through `main.py` (single entrypoint):

Mac/Linux:
```bash
source venv/bin/activate
python main.py <pdf_path>
```

Windows (CMD):
```bat
call venv\Scripts\activate.bat
python main.py <pdf_path>
```

## Script Generation Modes

### 1) Manual LLM mode (default)

No API key required.

```bash
python main.py assets/example.pdf
```

Flow:
1. App copies prompt + parsed PDF text to clipboard
2. Paste into your LLM of choice
3. Paste generated script back into terminal
4. Enter `END` on its own line to submit

### 2) OpenAI API mode

Requires `OPENAI_API_KEY`.

```bash
python main.py assets/example.pdf --use-openai-api
```

## Optional Main Arguments

- `<pdf_path>` (required positional argument)
- `--use-openai-api`
- `--voice-model` (default: `en_US-hfc_male-medium.onnx`)
- `--background-video` (default: `assets/background.mp4`)

Example:

```bash
python main.py <pdf_path> --use-openai-api --voice-model <voice_model_name> --background-video <background_video_path>.mp4
```

Notes:
- Default Piper model files are auto-downloaded to `voices/` if missing.
- Custom Piper voice models should exist in `voices/` as:
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
python test.py -video tests/tts/output.wav tests/video/test.mp4 tests/pdf/image_1.png
```

Test outputs are written to:
- `tests/pdf/`
- `tests/llm/`
- `tests/tts/`
- `tests/video/`

## Future Extensions

### Semantic image alignment per sentence

A high-impact next step is to align on-screen visuals with the current narration sentence instead of showing extracted PDF images in simple sequence.

Concept:
1. Split the generated script into sentence-level segments with timestamps.
2. Build semantic embeddings for each sentence and each available visual candidate:
   - extracted PDF figures
   - optional external image/video candidates
3. Match each sentence to the most relevant visual using embedding similarity.
4. Render the timeline so visuals change exactly when sentence topics change.

Why this is better:
- Stronger narrative coherence (visuals match what is being said now)
- Higher viewer retention
- Better educational clarity for technical papers

Tradeoffs and cost:
- Significantly higher compute cost (embedding generation + matching + timeline optimization)
- More memory/storage for indexing visual candidates
- Additional latency at generation time
- Potential need for reranking or quality filters to avoid weak matches

This feature would likely require a more advanced retrieval pipeline and careful optimization to keep runtime practical.

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
├── voices/                 # Piper voice models (auto-downloaded)
├── outputs/
│   └── <input_pdf_name>.mp4
├── temp/                   # transient media during run (cleaned after success)
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
