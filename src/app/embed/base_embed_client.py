from collections.abc import Sequence
from typing import Protocol


class EmbeddingModel(Protocol):
    def embed_query(
        self,
        text: str,
    ) -> list[float]: ...

    def embed_document(
        self,
        text: str,
    ) -> list[float]: ...

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]: ...
