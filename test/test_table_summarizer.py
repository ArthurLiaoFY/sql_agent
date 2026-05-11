import json
import os

from dotenv import load_dotenv

from app.llm.openai_llm_client import OpenAILLMClient
from app.table_summarizer import TableSchemaSummarizer

load_dotenv()
result = {}

summarizer = TableSchemaSummarizer(
    llm_client=OpenAILLMClient(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        model_name=os.getenv("LLM_MODEL_NAME"),
    )
)
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
