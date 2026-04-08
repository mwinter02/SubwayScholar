import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


class LLMModule:
    def generate_script(self, text: str) -> str:
        """Returns a short-form narration script"""
        load_dotenv()

        cleaned_text = self._normalize_text(text)
        if not cleaned_text:
            return "No usable text was provided from the paper."

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._build_fallback_script(cleaned_text)

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

    def _generate_final_script(self, client: OpenAI, source_text: str) -> str:
        prompt = (
            "Summarize the following research content into a short, engaging script "
            "for a 1-2 minute video. Use simple language. Keep it concise and interesting. "
            "Target 60-120 seconds, max 300 words, and preserve accuracy."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You write clear, engaging, accurate short-form narration scripts.",
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nResearch content:\n{source_text}",
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
