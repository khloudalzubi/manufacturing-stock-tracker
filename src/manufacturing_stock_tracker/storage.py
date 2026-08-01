"""SQLite persistence for repeated manufacturing watchlist snapshots."""

from pathlib import Path
import json
import sqlite3


DEFAULT_DB_PATH = Path("data") / "tracker.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS quote_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collected_at TEXT NOT NULL,
    symbols TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    average_price REAL NOT NULL,
    average_percent_change REAL,
    top_gainer_symbol TEXT,
    top_decliner_symbol TEXT
);

CREATE TABLE IF NOT EXISTS quote_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES quote_runs(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    name TEXT,
    exchange TEXT,
    currency TEXT,
    datetime TEXT,
    price REAL NOT NULL,
    percent_change REAL,
    volume INTEGER
);
"""


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create the SQLite database and tables when they do not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)


def save_quote_run(rows: list[dict], summary: dict, symbols: list[str], db_path: Path = DEFAULT_DB_PATH) -> int:
    """Save one processed quote collection run and return its database run id."""
    if not rows:
        raise ValueError("Cannot save an empty quote run to SQLite.")

    initialize_database(db_path)
    collected_at = str(rows[0]["collected_at"])

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO quote_runs (
                collected_at,
                symbols,
                row_count,
                average_price,
                average_percent_change,
                top_gainer_symbol,
                top_decliner_symbol
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                collected_at,
                json.dumps(symbols),
                summary["row_count"],
                summary["average_price"],
                summary["average_percent_change"],
                summary["top_gainer_symbol"],
                summary["top_decliner_symbol"],
            ),
        )
        run_id = int(cursor.lastrowid)
        connection.executemany(
            """
            INSERT INTO quote_rows (
                run_id,
                symbol,
                name,
                exchange,
                currency,
                datetime,
                price,
                percent_change,
                volume
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    row["symbol"],
                    row.get("name"),
                    row.get("exchange"),
                    row.get("currency"),
                    row.get("datetime"),
                    row["price"],
                    row.get("percent_change"),
                    row.get("volume"),
                )
                for row in rows
            ],
        )

    return run_id


def recent_quote_runs(db_path: Path = DEFAULT_DB_PATH, limit: int = 10) -> list[dict]:
    """Return recent quote run summaries from newest to oldest."""
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        records = connection.execute(
            """
            SELECT
                id,
                collected_at,
                symbols,
                row_count,
                average_price,
                average_percent_change,
                top_gainer_symbol,
                top_decliner_symbol
            FROM quote_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    runs = []
    for record in records:
        run = dict(record)
        run["symbols"] = ",".join(json.loads(run["symbols"]))
        runs.append(run)
    return runs


def quote_rows_for_run(run_id: int, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    """Return saved quote rows for one database run."""
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        records = connection.execute(
            """
            SELECT symbol, name, exchange, currency, datetime, price, percent_change, volume
            FROM quote_rows
            WHERE run_id = ?
            ORDER BY symbol
            """,
            (run_id,),
        ).fetchall()

    return [dict(record) for record in records]
