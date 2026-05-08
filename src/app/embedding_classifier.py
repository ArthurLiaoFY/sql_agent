import os
from typing import Any, Dict

import outlines
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from .prompts import (
    COMMON_COLUMN_PROFILE,
    NUMERIC_COLUMN_PROFILE,
    SHOULD_COLUMN_EMBED_SYS_PROMPT,
    STRING_COLUMN_PROFILE,
)

load_dotenv()


class EmbeddingDecision(BaseModel):
    needs_embedding: bool
    reason: str


class EmbeddingClassifier:
    """
    使用 OpenAI API 來決定資料庫欄位是否需要進行cell-level embedding。
    適用於Text-to-SQL任務的資料準備。
    """

    def __init__(
        self,
    ):
        """
        初始化 EmbeddingClassifier。
        """
        self.client = outlines.from_openai(
            client=OpenAI(
                base_url=os.getenv("BASE_URL"),
                api_key=os.getenv("API_KEY"),
            ),
            model_name=os.getenv("MODEL_NAME"),
        )

    def classify_column(self, column_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        決定欄位是否需要cell-level embedding。

        Args:
            column_profile: 欄位的profile資訊（同前）。

        Returns:
            dict: 包含 "needs_embedding" (bool) 和 "reason" (str) 的字典。
        """
        # 建構通用欄位描述
        common_profile = COMMON_COLUMN_PROFILE.format(**column_profile)

        # 根據欄位類型建構完整描述
        if column_profile["type"] == "numeric":
            user_message = NUMERIC_COLUMN_PROFILE.format(
                common_column_profile=common_profile, **column_profile
            )
            return {
                "needs_embedding": False,
                "reason": "numeric column",
            }
        elif column_profile["type"] == "string":
            user_message = STRING_COLUMN_PROFILE.format(
                common_column_profile=common_profile, **column_profile
            )
            prompt = (
                f"""System: {SHOULD_COLUMN_EMBED_SYS_PROMPT}\n\nUser: {user_message}\n\n"""
                + 'Assistant: Respond with JSON: {"needs_embedding": True or False, "reason": "string"}'
            )

            result_json = self.client(prompt, EmbeddingDecision)
            result = EmbeddingDecision.model_validate_json(result_json)
            return result.model_dump()
        else:
            return {
                "needs_embedding": False,
                "reason": f"Unsupported column type: {column_profile['type']}",
            }
