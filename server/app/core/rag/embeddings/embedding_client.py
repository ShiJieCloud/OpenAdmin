from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from typing import Optional


def create_embedding_client(
    model: str = "text-embedding-3",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    dimensions: int = 1536,
) -> OpenAIEmbeddings:
    """
    创建 OpenAI Embedding 客户端
    """
    if not api_key or not base_url:
        raise ValueError("api_key and base_url must be provided")

    embedding_client = OpenAIEmbeddings(
        model=model,
        api_key=api_key,
        base_url=base_url,
        check_embedding_ctx_length=False,
        dimensions=dimensions,
        model_kwargs={
            "encoding_format": "float"
        }
    )

    return embedding_client
