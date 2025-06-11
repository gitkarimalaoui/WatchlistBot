"""Wrapper around a local Llama model."""

import logging
from pathlib import Path

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
    """Lazily load and return the Llama instance."""
    global _llama
    if _llama is None:
        _llama = Llama(model_path=str(_MODEL_PATH))
    return _llama


def run_local_llm(prompt):
    """Return raw model output for the given prompt."""
    final_prompt = build_prompt(prompt)
    result = _load_model()(final_prompt)
    text = result["choices"][0]["text"]
    _logger.info(text.strip())
    return text
