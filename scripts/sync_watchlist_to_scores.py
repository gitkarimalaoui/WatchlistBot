#!/usr/bin/env python
"""
Synchronise la table `watchlist` vers `scores` :
- lit les tickers récents dans `watchlist`
- calcule un score (hook pluggable)
- upsert en batch dans `scores` (transaction)
Usage:
  python -m scripts.sync_watchlist_to_scores --limit 200 --fresh-only
"""

from __future__ import annotations
import argparse, json, os, sqlite3, sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

# ========= Référence DB unique (même que l'UI) =========
BASE_DIR = Path(__file__).resolve().parents[1]  # racine du repo
DB_PATH  = (BASE_DIR / "data" / "trades.db")

# -------- utilitaires DB --------
def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH.as_posix(), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS scores(
      symbol       TEXT NOT NULL,
      date         TEXT NOT NULL,
      score        REAL NOT NULL,
      details_json TEXT,
      PRIMARY KEY (symbol, date)
    );
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_scores_symbol_date
        ON scores(symbol, date);
    """)
    conn.commit()

def bulk_upsert_scores(conn: sqlite3.Connection,
                       rows: Iterable[Tuple[str, str, float, str]]) -> int:
    rows = list(rows)
    if not rows:
        return 0
    init_schema(conn)
    with conn:  # transaction
        conn.executemany("""
          INSERT INTO scores(symbol, date, score, details_json)
          VALUES(?,?,?,?)
          ON CONFLICT(symbol, date) DO UPDATE SET
            score=excluded.score,
            details_json=excluded.details_json;
        """, rows)
    return len(rows)

# -------- récupération des tickers depuis watchlist --------
def read_recent_watchlist(conn: sqlite3.Connection, limit: int | None, fresh_only: bool) -> List[str]:
    """
    Retourne une liste de symboles à scorer depuis `watchlist`.
    - fresh_only: ne prend que les lignes du dernier batch (MAX(created_at) ou MAX(date) si dispo)
    - sinon, distinct global (limité)
    """
    # détecter les colonnes disponibles
    cols = [r[1] for r in conn.execute("PRAGMA table_info(watchlist);").fetchall()]
    date_col = "created_at" if "created_at" in cols else ("date" if "date" in cols else None)

    if fresh_only and date_col:
        sql = f"""
        WITH last AS (SELECT MAX({date_col}) AS d FROM watchlist)
        SELECT DISTINCT symbol
        FROM watchlist, last
        WHERE {date_col} = last.d
        ORDER BY symbol
        """
        if limit:
            sql += " LIMIT ?"
            syms = [r[0] for r in conn.execute(sql, (limit,)).fetchall()]
        else:
            syms = [r[0] for r in conn.execute(sql).fetchall()]
    else:
        sql = "SELECT DISTINCT symbol FROM watchlist ORDER BY symbol"
        if limit:
            sql += " LIMIT ?"
            syms = [r[0] for r in conn.execute(sql, (limit,)).fetchall()]
        else:
            syms = [r[0] for r in conn.execute(sql).fetchall()]
    return syms

# -------- hook scoring (à brancher sur ton vrai moteur) --------
@dataclass
class ScoreResult:
    symbol: str
    score: float
    details: dict

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_score_stub(symbol: str) -> ScoreResult:
    """
    Placeholder SAFE: remplace par ton vrai calcul (RSI/EMA/Volume/VWAP…).
    Si tu as une fonction existante, par ex:
        from intelligence.ai_scorer import score_symbol
        return score_symbol(symbol)
    """
    # Heuristique ultra-simple pour garder le pipeline fonctionnel
    # (ici score aléatoire déterministe par symbole)
    base = sum(ord(c) for c in symbol) % 100
    score = float(base)  # 0..99
    details = {"source": "stub", "notes": "replace with real scorer", "features": {}}
    return ScoreResult(symbol=symbol, score=score, details=details)

def score_symbols(symbols: Iterable[str]) -> List[ScoreResult]:
    results: List[ScoreResult] = []
    for sym in symbols:
        try:
            r = compute_score_stub(sym)
            results.append(r)
        except Exception as e:
            # on ignore un symbole défaillant (best-effort)
            print(f"[WARN] scoring failed for {sym}: {e}", file=sys.stderr)
    return results

# -------- main --------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200, help="max tickers from watchlist")
    ap.add_argument("--fresh-only", action="store_true",
                    help="ne prendre que les tickers du dernier lot (MAX(created_at/date))")
    args = ap.parse_args()

    print(f"[INFO] DB: {DB_PATH.as_posix()}")
    conn = get_conn()

    # 1) récupérer les tickers depuis watchlist
    syms = read_recent_watchlist(conn, limit=args.limit, fresh_only=args.fresh_only)
    print(f"[INFO] watchlist symbols: {len(syms)}")

    if not syms:
        print("[INFO] rien à scorer (watchlist vide).")
        conn.close()
        return 0

    # 2) calculer les scores
    scored = score_symbols(syms)
    print(f"[INFO] scored: {len(scored)}")

    # 3) upsert batch dans `scores`
    rows = [(r.symbol, now_iso(), r.score, json.dumps(r.details)) for r in scored]
    n = bulk_upsert_scores(conn, rows)
    print(f"[INFO] upserted into scores: {n}")

    # 4) quick check
    chk = conn.execute("SELECT COUNT(*), MAX(date) FROM scores;").fetchone()
    print(f"[INFO] scores count={chk[0]} max_date={chk[1]}")
    conn.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
