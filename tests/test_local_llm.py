import os
import pytest

local_llm = pytest.importorskip("intelligence.local_llm")

def test_run_local_llm_missing_model(tmp_path):
    model = tmp_path / "model.bin"
    if not model.exists():
        pytest.skip("model file missing")
    result = local_llm.run_local_llm("Hello", model_path=str(model))
    assert isinstance(result, str)
