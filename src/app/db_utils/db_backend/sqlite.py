from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable, List, Optional

_READONLY_SQL = re.compile(r"^\s*(?:WITH|SELECT)\b", re.IGNORECASE)


class SQLiteConnection:
    """SQLite 只讀連線。

    默認以只讀模式開啟資料庫，並限制只能執行讀取查詢。
    """

    def __init__(self, database_path: str | Path, readonly: bool = True) -> None:
        self.database_path = Path(database_path)
        if not self.database_path.exists():
            raise FileNotFoundError(f"SQLite 資料庫不存在: {self.database_path}")

        if readonly:
            uri = f"file:{self.database_path.as_posix()}?mode=ro"
            self._conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        else:
            self._conn = sqlite3.connect(self.database_path, check_same_thread=False)

        self._conn.row_factory = sqlite3.Row
        self._readonly = readonly

    def __enter__(self) -> "SQLiteConnection":
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

    def execute_query(self, sql: str, params: Optional[Iterable[Any]] = None) -> sqlite3.Cursor:
        self._validate_readonly_query(sql)
        return self._conn.execute(sql, tuple(params or []))

    def fetch_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[sqlite3.Row]:
        cursor = self.execute_query(sql, params)
        return cursor.fetchone()

    def fetch_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[sqlite3.Row]:
        cursor = self.execute_query(sql, params)
        return cursor.fetchall()

    def fetch_all_dicts(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[dict[str, Any]]:
        rows = self.fetch_all(sql, params)
        return [dict(row) for row in rows]

    def list_tables(self) -> List[str]:
        rows = self.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        return [row[0] for row in rows]

    def list_columns(self, table_name: str) -> List[str]:
        quoted_name = '"' + table_name.replace('"', '""') + '"'
        rows = self.fetch_all(f"PRAGMA table_info({quoted_name})")
        return [row[1] for row in rows]
