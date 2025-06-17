from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

# ---- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "project_tracker.db"
META_PATH = PROJECT_ROOT / "config" / "meta_ia.json"

BASE_URL = "https://api.fda.gov/drug/drugsfda.json"
HEADERS = {"User-Agent": "WatchlistBot"}


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fda_approvals (
            application_number TEXT PRIMARY KEY,
            sponsor_name TEXT,
            substance_name TEXT,
            brand_name TEXT,
            submission_status_date TEXT,
            pharm_class TEXT,
            route TEXT,
            dosage_form TEXT,
            marketing_status TEXT,
            product_ndc TEXT,
            last_update TEXT
        )
        """
    )
    conn.commit()


def _fetch_page(params: Dict[str, Any]) -> Dict[str, Any]:
    if requests is None:
        raise ImportError("requests package is required")
    resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _parse_results(results: Iterable[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for entry in results:
        app_no = entry.get("application_number", "")
        sponsor = entry.get("sponsor_name", "")

        submission_date: Optional[str] = None
        for sub in entry.get("submissions", []):
            if sub.get("submission_status") == "AP":
                submission_date = sub.get("submission_status_date")
                break

        product = (entry.get("products") or [{}])[0]
        brand = product.get("brand_name", "")
        marketing = product.get("marketing_status", "")
        route = product.get("route", "")
        dosage = product.get("dosage_form", "")
        openfda = product.get("openfda", {})
        substance = ", ".join(openfda.get("substance_name", [])) if openfda else ""
        pharm_class = ", ".join(openfda.get("pharm_class_epc", [])) if openfda else ""
        ndc = ", ".join(openfda.get("product_ndc", [])) if openfda else ""

        rows.append(
            {
                "application_number": app_no,
                "sponsor_name": sponsor,
                "substance_name": substance,
                "brand_name": brand,
                "submission_status_date": submission_date,
                "pharm_class": pharm_class,
                "route": route,
                "dosage_form": dosage,
                "marketing_status": marketing,
                "product_ndc": ndc,
                "last_update": datetime.utcnow().isoformat(),
            }
        )
    return rows


def fetch_fda_data(
    limit: int = 100,
    *,
    start_date: Optional[str] = None,
    verbose: bool = False,
    link_to_watchlist: bool = False,
    db_path: Path = DB_PATH,
) -> int:
    """Fetch FDA approvals and store them in SQLite.

    Parameters
    ----------
    limit : int
        Number of records per API call.
    start_date : str, optional
        Filter approvals from this date (YYYY-MM-DD).
    verbose : bool
        Print progress information.
    link_to_watchlist : bool
        When True, also export brand names to ``meta_ia.json``.
    db_path : Path
        Location of the SQLite database.

    Returns
    -------
    int
        Number of records inserted.
    """
    search = 'submissions.submission_status:"AP"'
    if start_date:
        search += f'+submission_status_date:[{start_date}+TO+*]'

    params = {"search": search, "limit": 1}
    data = _fetch_page(params)
    total = data.get("meta", {}).get("results", {}).get("total", 0)

    if verbose:
        print(f"Total records: {total}")

    conn = sqlite3.connect(db_path)
    _ensure_table(conn)

    inserted = 0
    for skip in range(0, total, limit):
        params = {"search": search, "limit": limit, "skip": skip}
        page = _fetch_page(params)
        results = page.get("results", [])
        rows = _parse_results(results)
        for row in rows:
            conn.execute(
                """
                INSERT OR IGNORE INTO fda_approvals (
                    application_number, sponsor_name, substance_name,
                    brand_name, submission_status_date, pharm_class,
                    route, dosage_form, marketing_status, product_ndc, last_update
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["application_number"],
                    row["sponsor_name"],
                    row["substance_name"],
                    row["brand_name"],
                    row["submission_status_date"],
                    row["pharm_class"],
                    row["route"],
                    row["dosage_form"],
                    row["marketing_status"],
                    row["product_ndc"],
                    row["last_update"],
                ),
            )
            inserted += 1
        conn.commit()
        if verbose:
            print(f"Fetched {min(skip + limit, total)} / {total}")

    if link_to_watchlist:
        _export_to_meta(conn)

    conn.close()
    if verbose:
        print(f"Inserted {inserted} records")
    return inserted


def _export_to_meta(conn: sqlite3.Connection) -> None:
    cur = conn.execute(
        "SELECT brand_name, product_ndc FROM fda_approvals WHERE brand_name != ''"
    )
    data = {row[0]: {"fda_ndc": row[1]} for row in cur.fetchall()}
    if META_PATH.exists():
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    else:
        existing = {}
    existing.update(data)
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    import argparse

    parser = argparse.ArgumentParser(description="Fetch FDA approvals")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--start-date", type=str, help="Filter from this date")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--link-to-watchlist", action="store_true")
    args = parser.parse_args()

    fetch_fda_data(
        limit=args.limit,
        start_date=args.start_date,
        verbose=args.verbose,
        link_to_watchlist=args.link_to_watchlist,
    )
