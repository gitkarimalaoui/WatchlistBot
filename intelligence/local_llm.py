"""Wrapper around a local Llama model."""

import logging
import time
from pathlib import Path
from typing import Callable, List, Optional

from .token_utils import count_tokens

from llama_cpp import Llama
from scripts.run_chatgpt_batch import build_prompt

_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "mistral"
    / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
)

_LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "local_llm.log"

_logger = logging.getLogger(__name__)
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

_llama = None


def _load_model() -> Llama:
    global _llama
    if _llama is None:
        _llama = Llama(
            model_path=str(_MODEL_PATH),
            n_ctx=2048,
            n_threads=4,
            n_batch=128,
            verbose=True,
        )
    return _llama


def _send_prompt(prompt: str, stop: Optional[List[str]] = None) -> str:
    """Send a prompt string directly to the local model and return the raw text."""
    if stop is None:
        stop = ["</s>"]
    _logger.info("Prompt:\n%s", prompt)
    result = _load_model()(
        prompt=prompt,
        max_tokens=512,
        temperature=0.7,
        stop=stop,
    )
    text = result["choices"][0]["text"].strip()
    _logger.info("Response:\n%s", text)
    return text


def run_local_llm(prompt, stop: Optional[List[str]] = None, **kwargs):
    """Return raw model output for the given prompt list."""
    final_prompt = build_prompt(prompt)
    return _send_prompt(final_prompt, stop=stop)


def _split_into_chunks(text: str, max_tokens: int = 1800) -> List[str]:
    """Split large text into chunks of roughly ``max_tokens`` tokens."""
    lines = text.splitlines()
    chunks = []
    current: List[str] = []
    tokens = 0
    for line in lines:
        line_tokens = count_tokens(line)
        if tokens + line_tokens > max_tokens and current:
            chunks.append("\n".join(current))
            current = [line]
            tokens = line_tokens
        else:
            current.append(line)
            tokens += line_tokens
    if current:
        chunks.append("\n".join(current))
    return chunks


def chunk_and_query_local_llm(
    full_prompt,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    *,
    stop: Optional[List[str]] = None,
) -> str:
    """Send one or multiple prompt chunks to the local LLM.

    Parameters
    ----------
    full_prompt:
        Liste de prompts déjà séparés ou texte complet à découper.
    progress_callback:
        Optional callback receiving ``(current_chunk, total_chunks)`` after each
        successful call.
    """
    if isinstance(full_prompt, list):
        chunks = full_prompt
    else:
        chunks = _split_into_chunks(full_prompt)
    responses = []
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        _logger.info("Processing chunk %s/%s", i, total)
        try:
            responses.append(_send_prompt(chunk, stop=stop))
        except Exception as exc:
            _logger.error("Chunk %s failed: %s", i, exc)
            responses.append(f"[ERROR: {exc}]")
        if progress_callback:
            progress_callback(i, total)
        time.sleep(1)
    return "\n".join(responses)
