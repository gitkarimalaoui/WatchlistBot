import types
import sys

# ensure llama_cpp dummy for token_utils import path (in case local_llm import occurs later)
if "llama_cpp" not in sys.modules:
    dummy = types.ModuleType("llama_cpp")

    class DummyLlama:
        @staticmethod
        def tokenize(data: bytes, add_bos: bool = False):
            return data.decode().split()

    dummy.Llama = DummyLlama
    sys.modules["llama_cpp"] = dummy

from intelligence.token_utils import count_tokens
from scripts.run_chatgpt_batch import build_prompt, PROMPT_INSTRUCTIONS


def test_build_prompt_token_limit():
    symbols = [{"symbol": f"SYM{i}", "desc": "word " * 50} for i in range(50)]
    prompts = build_prompt(symbols, max_tokens=200)
    if isinstance(prompts, str):
        prompts = [prompts]
    for pr in prompts:
        assert count_tokens(pr) <= 200
        # ensure instruction prefix present
        assert PROMPT_INSTRUCTIONS.splitlines()[0] in pr
