import os
import pytest

local_llm = pytest.importorskip("intelligence.local_llm")

def test_run_local_llm_missing_model(tmp_path):
    model = tmp_path / "model.bin"
    if not model.exists():
        pytest.skip("model file missing")
    result = local_llm.run_local_llm("Hello", model_path=str(model))
    assert isinstance(result, str)


def test_chunk_and_query(monkeypatch):
    calls = []

    def fake_send(prompt):
        calls.append(prompt)
        return f"resp{len(calls)}"

    monkeypatch.setattr(local_llm, "_send_prompt", fake_send)
    text = " ".join(["a"] * 1500) + "\n" + " ".join(["b"] * 1500) + "\n" + " ".join(["c"] * 1500)
    result = local_llm.chunk_and_query_local_llm(text)
    assert result == "resp1\nresp2\nresp3"
    assert len(calls) == 3

