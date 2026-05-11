from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

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

    def list_column_type(self, table_name: str) -> Dict[str, str]:
        rows = self.fetch_all(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position",
            (table_name,),
        )
        return {
            row["column_name"] if isinstance(row, dict) else row[0]: row["data_type"]
            if isinstance(row, dict)
            else row[1]
            for row in rows
        }

def list_table_foreign_key_relationship(
    self,
    table_name: str,
) -> dict[str, str]:
    rows = self.fetch_all(
        """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.constraint_schema = kcu.constraint_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.constraint_schema = tc.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = %s
        """,
        (table_name,),
    )

    relationships = {}

    for row in rows:
        if isinstance(row, dict):
            source_column = row["column_name"]
            foreign_table = row["foreign_table_name"]
            foreign_column = row["foreign_column_name"]
        else:
            source_column = row[0]
            foreign_table = row[1]
            foreign_column = row[2]

        relationships[
            f"{table_name}.{source_column}"
        ] = f"{foreign_table}.{foreign_column}"

    return relationships