from pathlib import Path
from typing import Optional

from modules.llm_module import LLMModule


def run_llm_module_test(
    text_path: str, output_dir: Optional[Path] = None, use_api: bool = True
) -> dict:
    input_path = Path(text_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Text file not found: {text_path}")

    target_dir = output_dir or Path("tests/llm")
    target_dir.mkdir(parents=True, exist_ok=True)

    source_text = input_path.read_text(encoding="utf-8")
    module = LLMModule()
    script = module.generate_script(source_text, use_api=use_api)

    script_output = target_dir / "generated_script.txt"
    script_output.write_text(script, encoding="utf-8")

    return {
        "script_path": str(script_output),
    }
