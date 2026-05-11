from typing import Type

import outlines
from openai import OpenAI
from pydantic import BaseModel

from .base_llm_client import BaseLLMClient


class OpenAILLMClient(BaseLLMClient):
    def __init__(self, base_url: str, api_key: str, model_name: str) -> None:
        self.model_name = model_name

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self.structured_client = outlines.from_openai(
            client=self.client,
            model_name=model_name,
        )

    def invoke(
        self,
        input_query: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": input_query,
                }
            ],
        )

        return response.choices[0].message.content or ""

    def invoke_structured(
        self,
        input_query: str,
        output_schema: Type[BaseModel],
    ) -> BaseModel:

        return self.structured_client(input_query, output_schema)
