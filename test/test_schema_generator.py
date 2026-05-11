# %%
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json

from app.schema_generator import SchemaGenerator

with open("./test/test_data/profile_results.json", "r", encoding="utf-8") as f:
    profile_dicts = json.load(f)

schemas = {}
sg = SchemaGenerator()
for table, profile_dict in profile_dicts.items():
    schemas[table] = sg.generate_schemas(profile_dict)

# 儲存到檔案
with open("test/test_data/test_schema_output.json", "w", encoding="utf-8") as f:
    json.dump(schemas, f, indent=4, ensure_ascii=False)

print("\nSchemas saved to test/test_schema_output.json")

# %%
