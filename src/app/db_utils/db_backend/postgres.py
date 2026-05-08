from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional, Dict

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None

_READONLY_SQL = re.compile(r"^\s*(?:WITH|SELECT)\b", re.IGNORECASE)


class PostgresConnection:
    """PostgreSQL 只讀查詢連線。"""

    def __init__(self, dsn: str, readonly: bool = True) -> None:
        if psycopg is None:
            raise ImportError(
                "PostgreSQL support requires psycopg. Install with `pip install psycopg[binary]`."
            )

        self._conn = psycopg.connect(dsn)
        self._readonly = readonly

        if self._readonly:
            with self._conn.cursor() as cursor:
                cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")

    def __enter__(self) -> "PostgresConnection":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if self._conn:
            self._conn.close()

    def _validate_readonly_query(self, sql: str) -> None:
        if self._readonly and not _READONLY_SQL.match(sql):
            raise ValueError(
                "只允許執行讀取查詢 (SELECT / WITH)，不允許新增欄位、更新或刪除等變更語句。"
            )

    def execute_query(
        self, sql: str, params: Optional[Iterable[Any]] = None
    ) -> "psycopg.Cursor":
        self._validate_readonly_query(sql)
        cursor = self._conn.cursor(row_factory=dict_row)
        cursor.execute(sql, tuple(params or []))
        return cursor

    def fetch_one(
        self, sql: str, params: Optional[Iterable[Any]] = None
    ) -> Optional[Any]:
        cursor = self.execute_query(sql, params)
        return cursor.fetchone()

    def fetch_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Any]:
        cursor = self.execute_query(sql, params)
        return cursor.fetchall()

    def fetch_all_dicts(
        self, sql: str, params: Optional[Iterable[Any]] = None
    ) -> List[dict[str, Any]]:
        rows = self.fetch_all(sql, params)
        return [dict(row) if not isinstance(row, dict) else row for row in rows]

    def list_tables(self) -> List[str]:
        rows = self.fetch_all(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
        )
        return [row["table_name"] if isinstance(row, dict) else row[0] for row in rows]

    def list_columns(self, table_name: str) -> List[str]:
        rows = self.fetch_all(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position",
            (table_name,),
        )
        return [row["column_name"] if isinstance(row, dict) else row[0] for row in rows]

    def list_column_type(self, table_name: str) -> List[str]:
        pass
