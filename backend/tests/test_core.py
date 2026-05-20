from app.core import EMBEDDING_BATCH_SIZE, QdrantStore, RedisCache, build_point, get_langfuse_client, observe


def test_core_wrappers_import_and_build() -> None:
    cache = RedisCache()
    store = QdrantStore()
    point = build_point(vector=[0.0] * 3, payload={"source": "test"})
    langfuse_client = get_langfuse_client()

    assert EMBEDDING_BATCH_SIZE == 100
    assert cache is not None
    assert store is not None
    assert point.payload == {"source": "test"}
    assert callable(observe)
    assert get_langfuse_client() is langfuse_client
