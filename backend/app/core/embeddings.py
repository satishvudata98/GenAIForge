from collections.abc import Sequence

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, InternalServerError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

EMBEDDING_BATCH_SIZE = 100

settings = get_settings()


def _get_client() -> AsyncOpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate embeddings.")
    return AsyncOpenAI(api_key=settings.openai_api_key)


@retry(
    retry=retry_if_exception_type(
        (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def _embed_batch(texts: Sequence[str]) -> list[list[float]]:
    response = await _get_client().embeddings.create(
        model=settings.embedding_model,
        input=list(texts),
    )
    return [item.embedding for item in response.data]


async def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []

    vectors: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        vectors.extend(await _embed_batch(batch))
    return vectors
