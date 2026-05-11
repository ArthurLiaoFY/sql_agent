# %%
import json
import os

from app.db_utils.db_connection import DatabaseConnection
from app.table_profiler import TableProfiler

print("Connecting to database...")
db = DatabaseConnection.from_settings_file("./src/config/db_settings.yaml")

for table_name in db.list_tables():
    result = db.list_table_foreign_key_relationship(table_name=table_name)
    print(table_name)
    print(result, "\n\n")
