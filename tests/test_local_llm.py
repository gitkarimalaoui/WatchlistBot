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
import sqlite3
from scripts import run_chatgpt_batch as batch


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


def test_run_local_ticker_by_ticker(monkeypatch):
    prompts = []

    def fake_send(prompt, stop=None):
        prompts.append(prompt)
        symbol = "AAA" if len(prompts) == 1 else "BBB"
        return (
            '{"symbol": "%s", "sentiment": "bullish", "score": 5, "summary": "ok"}'
            % symbol
        )

    monkeypatch.setattr(local_llm, "_send_prompt", fake_send)

    entries = [
        {"symbol": "AAA", "desc": "foo"},
        {"symbol": "BBB", "desc": "bar"},
    ]
    progress = []

    def cb(i, total):
        progress.append((i, total))

    res = local_llm.run_local_ticker_by_ticker(entries, progress_callback=cb)

    assert res == [
        {"symbol": "AAA", "sentiment": "bullish", "score": 5, "summary": "ok"},
        {"symbol": "BBB", "sentiment": "bullish", "score": 5, "summary": "ok"},
    ]
    assert progress == [(1, 2), (2, 2)]
    assert prompts[0].startswith("[INST]") and prompts[0].endswith("[/INST]")


def test_save_scores_from_response_objects(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE news_score (symbol TEXT PRIMARY KEY, summary TEXT, score INTEGER, sentiment TEXT, last_analyzed DATETIME)"
    )
    conn.execute(
        "CREATE TABLE watchlist (ticker TEXT UNIQUE, score INTEGER)"
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(batch, "DB_PATH", db)

    data = [
        {
            "symbol": "AAA",
            "sentiment": "bullish",
            "score": 7,
            "summary": "ok",
        }
    ]

    batch.save_scores_from_response(data)

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT summary, score, sentiment FROM news_score WHERE symbol='AAA'"
    ).fetchone()
    conn.close()

    assert row == ("ok", 7, "bullish")


def test_save_scores_from_response_json_string(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE news_score (symbol TEXT PRIMARY KEY, summary TEXT, score INTEGER, sentiment TEXT, last_analyzed DATETIME)"
    )
    conn.execute(
        "CREATE TABLE watchlist (ticker TEXT UNIQUE, score INTEGER)"
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(batch, "DB_PATH", db)

    json_data = "[{\"symbol\": \"AAA\", \"sentiment\": \"bullish\", \"score\": 9, \"summary\": \"ok\"}]"

    batch.save_scores_from_response(json_data)

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT summary, score, sentiment FROM news_score WHERE symbol='AAA'"
    ).fetchone()
    conn.close()

    assert row == ("ok", 9, "bullish")
