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
    global _llama
    if _llama is None:
        _llama = Llama(
            model_path=str(_MODEL_PATH),
            n_ctx=2048,
            n_threads=4,
            n_batch=128,
            verbose=True
        )
    return _llama

def run_local_llm(prompt):
    """Return raw model output for the given prompt list."""
    final_prompt = build_prompt(prompt)
    result = _load_model()(
        prompt=final_prompt,
        max_tokens=512,
        temperature=0.7,
        stop=["</s>", "|"],
    )
    text = result["choices"][0]["text"].strip()
    _logger.info(text)
    return text
