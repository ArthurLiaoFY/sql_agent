COMMON_COLUMN_PROFILE = """
Column {column_name} (column type: {type}) stands for {desc}.
This column has {null_count} NULL values out of {total_records} records.
There are {distinct_count} distinct values (distinct ratio: {distinct_ratio}).
The most common non-NULL column values are {samples}.
"""

NUMERIC_COLUMN_PROFILE = """
{common_column_profile}
The values in this column follow the statistics below:
- min: {min}
- max: {max}
- avg: {avg}
- median: {median}
"""

STRING_COLUMN_PROFILE = """
{common_column_profile}
The length of the cell values ranges from {min_length} to {max_length}.
"""

SHOULD_COLUMN_EMBED_SYS_PROMPT = """
You are a data intelligence system for Text-to-SQL and data cataloging.

Your task is to decide whether a database column requires CELL-LEVEL EMBEDDING for its values.

Cell embedding means embedding individual cell values (not schema-level embeddings).
It is useful only when values carry semantic meaning or similarity structure.

Decision Rules:


1. Identifier detection:
   If column description contains words like:
   "id", "identifier", "code", "key", "uuid"
   → NOT suitable for cell embedding

2. Value pattern check (based on samples):
   - Long numeric / structured codes → NOT suitable
   - UUID-like / hash-like strings → NOT suitable
   - Natural language / categories → suitable

3. Semantic usefulness:
   Cell embedding is useful only if values have semantic similarity
   (e.g., names, categories, descriptions)

   It is NOT useful for pure identifiers or unique row keys.

"""
