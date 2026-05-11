import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# 初始化客戶端
# 因為是本地端，api_key 通常隨便填寫即可（除非你有設定認證）
client = OpenAI(
    base_url=os.getenv("EMBED_BASE_URL"), api_key=os.getenv("EMBED_API_KEY")
)


def get_embedding(text):
    # 呼叫 embeddings 介面
    response = client.embeddings.create(model=os.getenv("EMBED_MODEL_NAME"), input=text)

    # 取得向量結果
    embedding = response.data[0].embedding
    return embedding


# 測試呼叫
text_to_embed = "這是一個測試文字，用來產生向量。"
vector = get_embedding(text_to_embed)

print(f"向量維度: {len(vector)}")
print(f"向量前 5 碼: {vector[:5]}")
