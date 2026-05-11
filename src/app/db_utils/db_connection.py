from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from app.db_utils.db_backend.postgres import PostgresConnection
from app.db_utils.db_backend.sqlite import SQLiteConnection


class DatabaseConnection:
    """通用資料庫連線。

    根據設定使用 SQLite 或 PostgreSQL，只讀模式下只允許查詢語句。
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        db_type = str(config.get("DB_TYPE", "sqlite")).strip().lower()

        if db_type in ("sqlite", "sqlite3"):
            database_path = config.get("DB_PATH")
            if not database_path:
                raise ValueError("SQLite 需要設定 DB_PATH。")
            self._backend = SQLiteConnection(database_path, readonly=True)
        elif db_type in ("postgres", "postgresql"):
            dsn = config.get("DB_DSN")
            if not dsn:
                dsn = self._build_postgres_dsn(config)
            self._backend = PostgresConnection(dsn, readonly=True)
        else:
            raise ValueError(f"不支援的 DB_TYPE: {db_type}")

        self.db_backend = db_type

    @classmethod
    def from_settings_file(cls, settings_path: str | Path) -> "DatabaseConnection":
        try:
            import yaml
        except ImportError as exc:
            raise ImportError("請先安裝 PyYAML，才能使用設定檔讀取。") from exc

        path = Path(settings_path)
        if not path.exists():
            raise FileNotFoundError(f"設定檔不存在: {path}")

        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        return cls(config)

    def _build_postgres_dsn(self, config: dict[str, Any]) -> str:
        user = config.get("DB_USER")
        password = config.get("DB_PASSWORD")
        host = config.get("DB_HOST", "localhost")
        port = config.get("DB_PORT", 5432)
        db_name = config.get("DB_NAME")

        if not db_name:
            raise ValueError("PostgreSQL 需要設定 DB_NAME。")
        if not user or not password:
            raise ValueError(
                "PostgreSQL 需要設定 DB_USER 和 DB_PASSWORD，或者直接提供 DB_DSN。"
            )

        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    def __enter__(self) -> "DatabaseConnection":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self._backend.close()

    def execute_query(self, sql: str, params: Optional[Iterable[Any]] = None) -> Any:
        return self._backend.execute_query(sql, params)

    def fetch_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Any:
        return self._backend.fetch_one(sql, params)

    def fetch_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Any]:
        return self._backend.fetch_all(sql, params)

    def fetch_all_dicts(
        self, sql: str, params: Optional[Iterable[Any]] = None
    ) -> List[dict[str, Any]]:
        return self._backend.fetch_all_dicts(sql, params)

    def list_tables(self) -> List[str]:
        return self._backend.list_tables()

    def list_columns(self, table_name: str) -> List[str]:
        return self._backend.list_columns(table_name)

    def list_column_type(self, table_name: str) -> Dict[str, str]:
        return self._backend.list_column_type(table_name)

    def list_table_foreign_key_relationship(self, table_name: str) -> Dict[str, str]:
        return self._backend.list_table_foreign_key_relationship(table_name)
