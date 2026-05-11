import os

from dotenv import load_dotenv

from app.llm.openai_llm_client import OpenAILLMClient

load_dotenv()

client = OpenAILLMClient(
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY"),
    model_name=os.getenv("LLM_MODEL_NAME"),
)

print(client.invoke(input_query="hi hello"))
