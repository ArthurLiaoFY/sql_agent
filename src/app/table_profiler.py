from __future__ import annotations

from typing import Any, Dict, List, Literal

from datasketch import MinHash

from app.db_utils.db_connection import DatabaseConnection
from app.utils import serialize_minhash


def shingles(text, k=3):
    text = text.lower()
    return {text[i : i + k] for i in range(len(text) - k + 1)}


def build_minhash(texts, num_perm=128):
    m = MinHash(num_perm=num_perm)

    if isinstance(texts, str):
        texts = [texts]

    for text in texts:
        for s in shingles(text.strip().lower()):
            m.update(s.encode("utf-8"))

    return serialize_minhash(m)


class TableProfiler:
    """SQL 資料表分析器。

    分析資料表中每個欄位的統計資訊，包括記錄數、NULL 值、不同值數量、
    欄位形狀（最小值、最大值等）、字元統計、常見前綴，以及樣本值。
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        db_column_meanings: Dict,
        table_name: str,
        minhash_sample_size: int = 1000,
    ) -> None:
        self.db = db_connection
        self.db_col_meanings = db_column_meanings
        self.table_name = table_name
        self.minhash_sample_size = minhash_sample_size

    def profile(self, sample_k: int = 5) -> Dict[str, Any]:
        """生成資料表分析報告。

        Args:
            sample_k: 樣本值數量，預設 5。

        Returns:
            包含分析結果的字典。
        """
        # 獲取總記錄數
        total_records = self.db.fetch_one(f"SELECT COUNT(*) FROM {self.table_name}")[0]

        # 獲取欄位列表
        columns = self.db.list_columns(self.table_name)
        column_type = self.db.list_column_type(self.table_name)

        # 分析每個欄位

        profile = {
            "table_name": self.table_name,
            "total_records": total_records,
            "columns": {},
        }

        for col in columns:
            col_profile = self._profile_column(
                column_name=col,
                column_type=column_type.get(col),
                total_records=total_records,
                sample_k=sample_k,
            )
            profile["columns"][col] = col_profile

        return profile

    def _profile_column(
        self,
        column_name: str,
        column_type: Literal["numeric", "string"],
        total_records: int,
        sample_k: int,
    ) -> Dict[str, Any]:
        """分析單個欄位。"""
        # NULL 數量
        null_count = self.db.fetch_one(
            f'SELECT COUNT(*) FROM {self.table_name} WHERE "{column_name}" IS NULL'
        )[0]

        # 不同值數量
        distinct_count = self.db.fetch_one(
            f'SELECT COUNT(DISTINCT "{column_name}") FROM {self.table_name}'
        )[0]

        # 樣本值（最常見的 k 個值）
        samples = self._get_samples(column_name, sample_k)

        # 基礎返回欄位
        result = {
            "type": column_type,
            "desc": self.db_col_meanings.get(f"{self.table_name}|{column_name}", ""),
            "null_count": null_count,
            "distinct_count": distinct_count,
            "distinct_ratio": round(distinct_count / total_records, ndigits=4),
            "samples": samples,
        }

        # 根據型別加入統計量
        if column_type == "numeric":
            result.update(self._get_numeric_stats(column_name=column_name))
        elif column_type == "string":
            result.update(self._get_string_stats(column_name=column_name))

        return result

    def _get_numeric_stats(self, column_name: str) -> Dict[str, Any]:
        """計算數值欄位統計量：min, max, avg, median。"""
        try:
            # 計算 min, max, avg
            row = self.db.fetch_one(
                f'SELECT MIN("{column_name}"), MAX("{column_name}"), AVG("{column_name}") FROM {self.table_name} WHERE "{column_name}" IS NOT NULL'
            )
            if row and row[0] is not None:
                min_val, max_val, avg_val = row[0], row[1], row[2]
            else:
                return {}

            # 計算中位數
            median_row = self.db.fetch_one(
                f"""SELECT "{column_name}" FROM {self.table_name} WHERE "{column_name}" IS NOT NULL ORDER BY "{column_name}" LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM {self.table_name} WHERE "{column_name}" IS NOT NULL)"""
            )
            median_val = median_row[0] if median_row else None

            return {
                "min": min_val,
                "max": max_val,
                "avg": avg_val,
                "median": median_val,
            }
        except Exception:
            return {}

    def _get_string_stats(self, column_name: str) -> Dict[str, Any]:
        """計算字串欄位統計量：min_length, max_length, minhash。"""
        try:
            length_stats = self.db.fetch_one(
                f'SELECT MIN(LENGTH("{column_name}")), MAX(LENGTH("{column_name}")) FROM {self.table_name} WHERE "{column_name}" IS NOT NULL'
            )
            if length_stats and length_stats[0] is not None:
                result = {
                    "min_length": length_stats[0],
                    "max_length": length_stats[1],
                }

                minhash = self._compute_minhash(column_name)
                if minhash:
                    result["minhash"] = minhash

                return result
            return {}
        except Exception:
            return {}

    def _compute_minhash(self, column_name: str) -> MinHash:
        """計算欄位的 minhash。"""
        try:
            # 取得樣本
            rows = self.db.fetch_all(
                f'SELECT DISTINCT "{column_name}" FROM {self.table_name} WHERE "{column_name}" IS NOT NULL LIMIT {self.minhash_sample_size}'
            )

            # 從樣本計算 minhash
            texts = [str(row[0]) for row in rows if row[0] is not None]
            return build_minhash(texts)
        except Exception:
            return None

    def _get_samples(self, column_name: str, k: int) -> List[Any]:
        """獲取最常見的 k 個樣本值。"""
        rows = self.db.fetch_all_dicts(
            f"""SELECT "{column_name}", COUNT(*) AS cnt FROM {self.table_name} WHERE "{column_name}" IS NOT NULL GROUP BY "{column_name}" ORDER BY cnt DESC LIMIT {k}"""
        )
        return [row[column_name] for row in rows]
