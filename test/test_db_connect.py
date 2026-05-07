# %%
import yaml

from app.db_utils.db_connection import DatabaseConnection

db = DatabaseConnection.from_settings_file(
    "/Users/wr80340/WorkSpace/sql_agent/src/config/settings.yaml"
)
with db:
    rows = db.fetch_all("SELECT * FROM frpm LIMIT 5")
    for row in rows:
        print(dict(row))
