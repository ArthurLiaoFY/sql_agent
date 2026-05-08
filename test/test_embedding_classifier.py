"""
測試 EmbeddingClassifier 的不同模型來源和結構化輸出功能。
"""

import json

from app.embedding_classifier import EmbeddingClassifier

with open(
    r"/Users/wr80340/WorkSpace/sql_agent/test/test_data/profile_results.json"
) as f:
    column_profile = json.load(f)


ec = EmbeddingClassifier()
for col_name, col_profile in column_profile.get("columns").items():
    res = ec.classify_column(
        column_profile={
            **{
                "column_name": col_name,
                "total_records": column_profile.get("total_records"),
            },
            **col_profile,
        }
    )
    print(res)
