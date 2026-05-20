from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar

from langfuse import Langfuse
from langfuse.decorators import observe as langfuse_observe

from app.config import get_settings

settings = get_settings()

WrappedCallable = TypeVar("WrappedCallable", bound=Callable[..., Any])


@lru_cache
def get_langfuse_client() -> Langfuse | None:
    if settings.langfuse_disabled:
        return None
    if not all(
        [
            settings.langfuse_host,
            settings.langfuse_public_key,
            settings.langfuse_secret_key,
        ]
    ):
        return None

    return Langfuse(
        host=str(settings.langfuse_host),
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
    )


def observe(*args: Any, **kwargs: Any):
    if settings.langfuse_disabled:
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def passthrough(func: WrappedCallable) -> WrappedCallable:
            return func

        return passthrough

    return langfuse_observe(*args, **kwargs)
