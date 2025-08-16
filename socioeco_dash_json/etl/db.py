
import sqlite3
from typing import Iterable, Dict, Any

RAW_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS raw_values ("
    "  country TEXT,"
    "  country_name TEXT,"
    "  code TEXT,"
    "  indicator_name TEXT,"
    "  date INTEGER,"
    "  value REAL,"
    "  PRIMARY KEY (country, code, date)"
    ");"
)

COMPOSITE_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS composite_values ("
    "  country TEXT,"
    "  composite TEXT,"
    "  date INTEGER,"
    "  value REAL,"
    "  PRIMARY KEY (country, composite, date)"
    ");"
)

def get_conn(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)

def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(RAW_TABLE_SQL)
    cur.execute(COMPOSITE_TABLE_SQL)
    conn.commit()

def upsert_raw(conn: sqlite3.Connection, rows: Iterable[Dict[str, Any]]) -> int:
    cur = conn.cursor()
    data = [
        (
            r.get("country"),
            r.get("country_name"),
            r.get("code"),
            r.get("indicator_name"),
            r.get("date"),
            r.get("value"),
        )
        for r in rows
    ]
    if not data:
        return 0
    cur.executemany(
        "INSERT OR REPLACE INTO raw_values(country,country_name,code,indicator_name,date,value) "
        "VALUES (?,?,?,?,?,?)",
        data,
    )
    conn.commit()
    return len(data)

def upsert_composite(conn: sqlite3.Connection, rows: Iterable[Dict[str, Any]]) -> int:
    cur = conn.cursor()
    data = [
        (r.get("country"), r.get("composite"), r.get("date"), r.get("value"))
        for r in rows
    ]
    if not data:
        return 0
    cur.executemany(
        "INSERT OR REPLACE INTO composite_values(country, composite, date, value) "
        "VALUES (?,?,?,?)",
        data,
    )
    conn.commit()
    return len(data)
