from types import SimpleNamespace

import automation.codex_watcher as cw


def test_model_handler_triggers(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cw, "open_codex_patch", lambda data, msg: calls.append((data, msg)))
    handler = cw.FinRLModelHandler(cw.open_codex_patch)

    model_file = tmp_path / "model.json"
    model_file.write_text('{"lr": 0.1}')

    event = SimpleNamespace(src_path=str(model_file), is_directory=False)
    handler.on_created(event)

    assert calls
    data, msg = calls[0]
    assert msg.startswith("New model file")
    assert data == {"lr": 0.1}


def test_log_handler_triggers(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cw, "open_codex_patch", lambda data, msg: calls.append((data, msg)))
    handler = cw.LogHandler(cw.open_codex_patch)

    log_file = tmp_path / "local_llm.log"
    log_file.write_text("line1\n")

    event = SimpleNamespace(src_path=str(log_file), is_directory=False)
    handler.on_modified(event)

    assert calls
    data, msg = calls[0]
    assert msg.startswith("Log update")
    assert "line1" in data
