# %%
import json
import os

from app.db_utils.db_connection import DatabaseConnection
from app.table_profiler import TableProfiler

db = DatabaseConnection.from_settings_file("./src/config/db_settings.yaml")

file_path = r"./data/dev_column_meaning.json"

with open(file_path, "r") as f:
    data = json.load(f)
# %%
tp = TableProfiler(
    db_connection=db,
    db_column_meanings=data,
    table_name="frpm",
)
profile_data = tp.profile(sample_k=5)

file_path = "./test/test_data/profile_results.json"

os.makedirs(os.path.dirname(file_path), exist_ok=True)

# 將資料存入 local
with open(file_path, "w", encoding="utf-8") as f:
    # indent=4 可以讓 JSON 格式漂亮排版，方便閱讀
    # ensure_ascii=False 確保中文等特殊字元不會變成亂碼
    json.dump(profile_data, f, indent=4, ensure_ascii=False)

print(f"成功將 Profile 資料儲存至：{file_path}")
