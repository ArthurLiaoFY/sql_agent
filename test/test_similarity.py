import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SCHEMA_PATH = Path(__file__).resolve().parent / "test_data" / "test_schema_output.json"


def get_openai_client() -> OpenAI:
    base_url = os.getenv("EMBED_BASE_URL") or os.getenv("BASE_URL")
    api_key = os.getenv("EMBED_API_KEY") or os.getenv("API_KEY")
    if not base_url or not api_key:
        raise RuntimeError(
            "Missing EMBED_BASE_URL/EMBED_API_KEY or BASE_URL/API_KEY in .env"
        )
    return OpenAI(base_url=base_url, api_key=api_key)


def get_embed_model() -> str:
    return os.getenv("EMBED_MODEL_NAME") or os.getenv("MODEL_NAME") or "bge-m3"


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def compute_similarity_matrix(vectors: list[list[float]]) -> list[list[float]]:
    size = len(vectors)
    matrix = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] = cosine_similarity(vectors[i], vectors[j])
    return matrix


def main() -> None:
    print("Loading schema output...")
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema_output = json.load(f)

    print(f"Loaded {len(schema_output)} columns")

    print("Initializing OpenAI client...")
    client = get_openai_client()
    model = get_embed_model()
    print(f"Using model: {model}")

    embeddings: dict[str, list[float]] = {}
    print("Generating embeddings...")
    for col_name, col_desc in schema_output.items():
        text = col_desc.get("short_schema") or col_desc.get("long_schema") or ""
        if not text.strip():
            print(f"Skipping {col_name}: no text")
            continue

        print(f"Embedding {col_name}...")
        response = client.embeddings.create(model=model, input=text)
        embedding = response.data[0].embedding
        embeddings[col_name] = embedding

    print(f"Generated embeddings for {len(embeddings)} columns")

    names = list(embeddings.keys())
    vectors = [embeddings[name] for name in names]
    print("Computing similarity matrix...")
    similarity_matrix = compute_similarity_matrix(vectors)

    print("Computed similarity matrix for columns:")
    for idx, name in enumerate(names):
        print(f"{idx + 1}. {name}")

    print("\nTop 10 most similar column pairs:")
    pairs = []
    n = len(names)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((similarity_matrix[i][j], names[i], names[j]))
    pairs.sort(reverse=True, key=lambda item: item[0])

    for score, a, b in pairs[:10]:
        print(f"{score:.4f}: {a} <-> {b}")

    print("\nExample similarity row for the first column:")
    if names:
        first_row = similarity_matrix[0]
        for j, score in enumerate(first_row):
            print(f"{names[0]} vs {names[j]} = {score:.4f}")


if __name__ == "__main__":
    main()
