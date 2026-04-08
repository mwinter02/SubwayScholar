import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


class LLMModule:
    MANUAL_PROMPT_PATH = Path("temp/manual_llm_prompt.txt")

    def generate_script(self, text: str, use_api: bool = False) -> str:
        """Returns a short-form narration script"""
        load_dotenv()

        cleaned_text = self._normalize_text(text)
        if not cleaned_text:
            return "No usable text was provided from the paper."

        if use_api:
            return self._generate_script_with_api(cleaned_text)

        return self._generate_script_manual(cleaned_text)

    def _generate_script_with_api(self, cleaned_text: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Use manual mode (default) or set the key."
            )

        client = OpenAI(api_key=api_key)
        chunks = self._chunk_text(cleaned_text, max_chars=3000)

        try:
            if len(chunks) > 1:
                chunk_summaries = [self._summarize_chunk(client, chunk) for chunk in chunks]
                source_text = "\n".join(chunk_summaries)
            else:
                source_text = chunks[0]

            script = self._generate_final_script(client, source_text)
            return self._clean_response(script)
        except Exception:
            return self._build_fallback_script(cleaned_text)

    def _generate_script_manual(self, cleaned_text: str) -> str:
        prompt_text = self._build_final_prompt(cleaned_text)

        self.MANUAL_PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.MANUAL_PROMPT_PATH.write_text(prompt_text, encoding="utf-8")

        copied = self._copy_to_clipboard(prompt_text)
        print("       Manual LLM mode enabled.")
        if copied:
            print("       Prompt + parsed PDF text copied to clipboard.")
        else:
            print("       Clipboard copy unavailable. Use saved prompt file instead.")

        print(f"       Prompt file: {self.MANUAL_PROMPT_PATH}")
        print("       Next steps:")
        print("       1. Open your LLM of choice.")
        print("       2. Paste the copied prompt (or prompt file contents) and submit.")
        print("       3. Paste the generated script below and press Enter to submit.")

        script = self._read_script_from_terminal()
        return script

    def _read_script_from_terminal(self) -> str:
        try:
            script = input().strip()
        except EOFError as exc:
            raise RuntimeError("No script text was provided in manual LLM mode.") from exc

        if not script:
            raise RuntimeError("No script text was provided in manual LLM mode.")

        return script

    def _copy_to_clipboard(self, text: str) -> bool:
        commands: List[List[str]] = []

        if sys.platform == "darwin":
            commands.append(["pbcopy"])
        elif os.name == "nt":
            commands.append(["clip"])
        else:
            if shutil.which("wl-copy"):
                commands.append(["wl-copy"])
            if shutil.which("xclip"):
                commands.append(["xclip", "-selection", "clipboard"])
            if shutil.which("xsel"):
                commands.append(["xsel", "--clipboard", "--input"])

        for command in commands:
            try:
                subprocess.run(command, input=text, text=True, check=True)
                return True
            except Exception:
                continue

        return False

    def _summarize_chunk(self, client: OpenAI, chunk: str) -> str:
        prompt = (
            "Summarize this research chunk in 3-5 concise bullet points. "
            "Focus on problem, method, findings, and significance."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You summarize technical research accurately and briefly.",
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nResearch chunk:\n{chunk}",
                },
            ],
            max_tokens=180,
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        return self._clean_response(content)

    def _build_final_prompt(self, source_text: str) -> str:
        return (
            "Summarize the following research content into a short, engaging script "
            "for a 1-2 minute video. Use simple language. Keep it concise and interesting. "
            "Target 60-120 seconds, max 300 words, and preserve accuracy. "
            "Return only the final narration script and no extra commentary.\n\n"
            f"Research content:\n{source_text}"
        )

    def _generate_final_script(self, client: OpenAI, source_text: str) -> str:
        prompt = self._build_final_prompt(source_text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You write clear, engaging, accurate short-form narration scripts.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=360,
            temperature=0.4,
        )

        content = response.choices[0].message.content or ""
        return content

    def _chunk_text(self, text: str, max_chars: int = 3000) -> List[str]:
        words = text.split()
        if not words:
            return [""]

        chunks: List[str] = []
        current_words: List[str] = []
        current_length = 0

        for word in words:
            word_length = len(word) + (1 if current_words else 0)
            if current_words and current_length + word_length > max_chars:
                chunks.append(" ".join(current_words))
                current_words = [word]
                current_length = len(word)
            else:
                current_words.append(word)
                current_length += word_length

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").split())

    def _clean_response(self, content: str) -> str:
        return " ".join((content or "").split())

    def _build_fallback_script(self, text: str) -> str:
        words = text.split()
        core = " ".join(words[:220])
        if len(words) > 220:
            core += " ..."

        fallback = (
            "In this short overview, we break down a research paper into its key idea, "
            "approach, and main findings. "
            f"{core} "
            "The core takeaway is how this work advances understanding and why it matters in practice."
        )

        return " ".join(fallback.split())
