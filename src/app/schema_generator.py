from collections import defaultdict
from typing import Any, Dict, List

from app.logger.logger import logger


class SchemaGenerator:
    """生成欄位 schema 的類別。

    根據欄位 profile 生成詳細的 schema 描述。
    """

    SCHEMA_TEMPLATE = """
Column description:\n{description}

Column statistics:\nColumn {column_name} has {null_count} NULL values out of {total_records} records.
There are {distinct_count} distinct values (distinct ratio: {distinct_ratio}).
{length_info}

Example values: \n{samples}
""".strip()

    def __init__(self):
        pass

    def generate_long_schema(self, column_profile: Dict[str, Any]) -> str:
        """生成詳細 schema 描述。"""
        desc = column_profile.get("desc", "").strip("#")
        column_name = column_profile.get("name", "")
        null_count = column_profile.get("null_count", 0)
        total_records = column_profile.get("total_records", 0)
        distinct_count = column_profile.get("distinct_count", 0)
        distinct_ratio = column_profile.get("distinct_ratio", 0.0)
        samples = column_profile.get("samples", [])

        length_info = self._generate_length_info(column_profile)

        return self.SCHEMA_TEMPLATE.format(
            description=desc,
            column_name=column_name,
            null_count=null_count,
            total_records=total_records,
            distinct_count=distinct_count,
            distinct_ratio=round(distinct_ratio, 4),
            length_info=length_info,
            samples=", ".join([str(sample) for sample in samples]),
        )

    def _generate_length_info(self, profile: Dict[str, Any]) -> str:
        """生成長度資訊。"""
        min_length = profile.get("min_length")
        max_length = profile.get("max_length")
        if min_length is not None and max_length is not None:
            if min_length == max_length:
                return f"The values are always {min_length} characters long."
            else:
                return f"The values range from {min_length} to {max_length} characters long."
        return ""

    def generate_schemas(
        self, profile_dict: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        """生成schema。"""
        schemas = defaultdict(str)
        for column_name, column_profile in profile_dict.items():
            logger.info(f"Generating {column_name} schema")
            schemas[column_name] = {
                "short_schema": column_profile.get("desc", "").strip("#"),
                "long_schema": self.generate_long_schema(column_profile),
            }
        return schemas
