from collections.abc import Sequence

from openai import OpenAI

from .base_embed_client import EmbeddingModel


class OpenAIEmbeddingClient(EmbeddingModel):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model_name: str,
    ) -> None:
        self.model_name = model_name

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def _embed(
        self,
        text: str,
    ) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )

        return response.data[0].embedding

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return self._embed(text)

    def embed_document(
        self,
        text: str,
    ) -> list[float]:
        return self._embed(text)

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=list(texts),
        )

        return [
            item.embedding
            for item in response.data
        ]