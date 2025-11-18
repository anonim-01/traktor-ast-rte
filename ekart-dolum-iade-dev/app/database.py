from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, Iterable, Optional

from .config import AppConfig

_SCHEMA_PATCHES = (
    ("sazan", "toplam_limit", "INTEGER", "0"),
    ("sazan", "guncel_limit", "INTEGER", "0"),
)


def _ensure_schema(connection: sqlite3.Connection) -> None:
    """Adds new columns to legacy dumps if they are missing."""
    cursor = connection.cursor()
    for table_name, column_name, column_type, default in _SCHEMA_PATCHES:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1] for row in cursor.fetchall()}
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default}"
            )
    connection.commit()
    cursor.close()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(AppConfig.database_path)
    connection.row_factory = sqlite3.Row
    _ensure_schema(connection)
    return connection


@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    finally:
        connection.close()


def execute(query: str, params: Optional[Iterable[Any]] = None) -> int:
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return int(cursor.lastrowid or 0)


def fetch_one(query: str, params: Optional[Iterable[Any]] = None) -> Optional[dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: Optional[Iterable[Any]] = None) -> list[dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
