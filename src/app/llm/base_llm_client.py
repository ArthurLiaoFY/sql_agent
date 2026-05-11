from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel


class BaseLLMClient(ABC):
    @abstractmethod
    def invoke(
        self,
        input_query: str,
    ) -> str:
        pass

    @abstractmethod
    def invoke_structured(
        self,
        input_query: str,
        output_schema: Type[BaseModel],
    ) -> BaseModel:
        pass
