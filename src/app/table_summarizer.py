import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.llm.base_llm_client import BaseLLMClient
from app.logger.logger import logger
from app.prompts import TABLE_SUMMARIZE_PROMPT

load_dotenv()


class TableSchemaSummarizer:
    """Summarize a schema JSON file into per-table reports using an LLM."""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def load_schema(self, schema_path: str | Path) -> dict[str, dict[str, Any]]:
        schema_path = Path(schema_path)
        with schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def summarize_table(
        self,
        table_name: str,
        column_map: dict[str, dict[str, str]],
        max_summary_chars: int,
    ) -> str:
        """Generate a concise table summary report from table column short_schema values."""
        rows = []
        for column_name, column_data in column_map.items():
            short_schema = column_data.get("short_schema", "").strip()
            if not short_schema:
                continue
            rows.append(f"- {column_name}: {short_schema}")

        prompt = TABLE_SUMMARIZE_PROMPT.format(
            max_summary_chars=max_summary_chars,
            table_name=table_name,
            column_descriptions=chr(10).join(rows),
        )
        logger.info(f"Summarizing table schema: {table_name}.")
        response_text = self._create_response(prompt)
        summary = self._trim_summary(response_text, max_summary_chars)
        return summary

    def summarize_schema_file(
        self,
        schema_path: str | Path,
        max_summary_chars: int = 1500,
    ) -> dict[str, str]:
        schema_data = self.load_schema(schema_path)
        result: dict[str, str] = {}
        for table_name, columns in schema_data.items():
            if not isinstance(columns, dict) or not columns:
                continue
            result[table_name] = self.summarize_table(
                table_name, columns, max_summary_chars=max_summary_chars
            )
        return result

    def _create_response(self, prompt: str) -> str:
        response = self.llm_client.invoke(input_query=prompt)
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text.strip()

        if isinstance(response, dict):
            if "output_text" in response:
                return response["output_text"].strip()
            if "output" in response and isinstance(response["output"], list):
                parts = []
                for item in response["output"]:
                    if isinstance(item, dict):
                        text = item.get("content")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return "".join(parts).strip()

        raise RuntimeError("Unable to extract text from LLM response")

    def _trim_summary(self, summary: str, max_chars: int) -> str:
        if len(summary) <= max_chars:
            return summary
        logger.warning("Summarize result too long, trimming...")
        trimmed = summary[:max_chars].rstrip()
        if " " in trimmed:
            trimmed = trimmed[: trimmed.rfind(" ")]
        return f"{trimmed}..."


def main() -> None:
    summarizer = TableSchemaSummarizer()
    schema_path = (
        Path(__file__).resolve().parent.parent.parent
        / "test"
        / "test_data"
        / "test_schema_output.json"
    )
    reports = summarizer.summarize_schema_file(schema_path)
    for table_name, report in reports.items():
        print(f"=== {table_name} ===")
        print(report)
        print()


if __name__ == "__main__":
    main()
