import os

from dotenv import load_dotenv

from app.embed.openai_embed_client import OpenAIEmbeddingClient

load_dotenv()


ec = OpenAIEmbeddingClient(
    base_url=os.getenv("EMBED_BASE_URL"),
    api_key=os.getenv("EMBED_API_KEY"),
    model_name=os.getenv("EMBED_MODEL_NAME"),
)


# 測試呼叫
text_to_embed = "這是一個測試文字，用來產生向量。"
vector = ec.embed_query(text=text_to_embed)

print(f"向量維度: {len(vector)}")
print(f"向量前 5 碼: {vector[:5]}")
