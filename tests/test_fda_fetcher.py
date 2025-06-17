import sqlite3
from pathlib import Path

import types

import utils.fda_fetcher as fda


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_fetch_fda_data(monkeypatch, tmp_path: Path):
    sample = {
        "results": [
            {
                "application_number": "NDA0001",
                "sponsor_name": "DemoPharma",
                "products": [
                    {
                        "brand_name": "DrugA",
                        "route": "ORAL",
                        "dosage_form": "TABLET",
                        "marketing_status": "Prescription",
                        "openfda": {
                            "substance_name": ["SubstanceA"],
                            "pharm_class_epc": ["ClassA"],
                            "product_ndc": ["0001-0001"]
                        }
                    }
                ],
                "submissions": [
                    {
                        "submission_status": "AP",
                        "submission_status_date": "2024-01-15"
                    }
                ]
            }
        ],
        "meta": {"results": {"total": 1}}
    }

    calls = []

    def dummy_get(url, headers=None, params=None, timeout=None):
        calls.append(params)
        return DummyResponse(sample)

    monkeypatch.setattr(fda, "requests", types.SimpleNamespace(get=dummy_get))
    db_file = tmp_path / "test.db"
    inserted = fda.fetch_fda_data(limit=1, db_path=db_file)

    assert inserted == 1
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT brand_name FROM fda_approvals").fetchone()
    conn.close()
    assert row[0] == "DrugA"
    assert calls


def test_fetch_fda_data_incremental(monkeypatch, tmp_path: Path):
    sample = {
        "results": [
            {
                "application_number": "NDA0001",
                "sponsor_name": "DemoPharma",
                "products": [
                    {
                        "brand_name": "DrugA",
                        "route": "ORAL",
                        "dosage_form": "TABLET",
                        "marketing_status": "Prescription",
                        "openfda": {
                            "substance_name": ["SubstanceA"],
                            "pharm_class_epc": ["ClassA"],
                            "product_ndc": ["0001-0001"],
                        },
                    }
                ],
                "submissions": [
                    {
                        "submission_status": "AP",
                        "submission_status_date": "2024-01-15",
                    }
                ],
            }
        ],
        "meta": {"results": {"total": 1}},
    }

    def dummy_get(url, headers=None, params=None, timeout=None):
        return DummyResponse(sample)

    monkeypatch.setattr(fda, "requests", types.SimpleNamespace(get=dummy_get))
    db_file = tmp_path / "test.db"
    first = fda.fetch_fda_data(limit=1, db_path=db_file)
    second = fda.fetch_fda_data(limit=1, db_path=db_file)

    assert first == 1
    assert second == 0

