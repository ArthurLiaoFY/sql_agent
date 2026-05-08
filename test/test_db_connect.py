from app.db_utils.db_connection import DatabaseConnection

# with DatabaseConnection.from_settings_file(
#     "/Users/wr80340/WorkSpace/sql_agent/src/config/db_settings.yaml"
# ) as db:
#     rows = db.fetch_all("SELECT * FROM frpm LIMIT 5")
#     for row in rows:
#         print(dict(row))

# with DatabaseConnection.from_settings_file(
#     "/Users/wr80340/WorkSpace/sql_agent/src/config/db_settings.yaml"
# ) as db:
#     rows = db.list_columns(table_name="frpm")
#     print(rows)

# with DatabaseConnection.from_settings_file(
#     "/Users/wr80340/WorkSpace/sql_agent/src/config/db_settings.yaml"
# ) as db:
#     rows = db.fetch_all_dicts('SELECT "CDSCode"  FROM frpm limit 5;')
#     print(rows)

with DatabaseConnection.from_settings_file(
    "/Users/wr80340/WorkSpace/sql_agent/src/config/db_settings.yaml"
) as db:
    rows = db.list_column_type(table_name="frpm")
    print(rows)
