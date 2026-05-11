import json

from app.table_summarizer import TableSchemaSummarizer

result = {}

summarizer = TableSchemaSummarizer()
reports = summarizer.summarize_schema_file("test/test_data/test_schema_output.json")

for table_name, report in reports.items():
    result[table_name] = report


file_path = "./test/test_data/table_summary.json"

# 將資料存入 local
with open(file_path, "w", encoding="utf-8") as f:
    # indent=4 可以讓 JSON 格式漂亮排版，方便閱讀
    # ensure_ascii=False 確保中文等特殊字元不會變成亂碼
    json.dump(result, f, indent=4, ensure_ascii=False)

print(f"成功將 Profile 資料儲存至：{file_path}")
