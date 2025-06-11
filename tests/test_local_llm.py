import os
import sys
import types
import pytest

if "llama_cpp" not in sys.modules:
    dummy = types.ModuleType("llama_cpp")

    class DummyLlama:
        @staticmethod
        def tokenize(data: bytes, add_bos: bool = False):
            text = data.decode().replace("\n", " \n ")
            return text.split()

    dummy.Llama = DummyLlama
    sys.modules["llama_cpp"] = dummy

from intelligence import local_llm
from intelligence.token_utils import count_tokens


def test_run_local_llm_missing_model(tmp_path):
    model = tmp_path / "model.bin"
    if not model.exists():
        pytest.skip("model file missing")
    result = local_llm.run_local_llm("Hello", model_path=str(model))
    assert isinstance(result, str)


def test_chunk_and_query(monkeypatch):
    calls = []
    progress = []

    def fake_send(prompt, stop=None):
        calls.append((prompt, stop))
        return f"resp{len(calls)}"

    monkeypatch.setattr(local_llm, "_send_prompt", fake_send)

    text = (
        " ".join(["a"] * 1500)
        + "\n"
        + " ".join(["b"] * 1500)
        + "\n"
        + " ".join(["c"] * 1500)
    )

    def cb(i, total):
        progress.append((i, total))

    result = local_llm.chunk_and_query_local_llm(text, progress_callback=cb)

    assert result == "resp1\nresp2\nresp3"
    assert len(calls) == 3
    assert progress == [(1, 3), (2, 3), (3, 3)]
    for prompt, stop in calls:
        assert count_tokens(prompt) <= 1800
        assert stop is None
