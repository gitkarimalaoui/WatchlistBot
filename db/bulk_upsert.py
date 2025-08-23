def bulk_upsert_scores(conn, rows):
    with conn:
        conn.executemany(
            """
            INSERT INTO scores(symbol, date, score, details_json)
            VALUES(?,?,?,?)
            ON CONFLICT(symbol, date) DO UPDATE SET
                score=excluded.score, details_json=excluded.details_json
            """,
            rows,
        )
