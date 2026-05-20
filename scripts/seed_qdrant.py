from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.dependencies import SessionLocal  # noqa: E402
from app.rag.ingestion import ingest_documents  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed a Qdrant collection with sample documents.")
    parser.add_argument(
        "--docs-dir",
        default=str(ROOT_DIR / "scripts" / "sample_docs"),
        help="Directory containing sample files to ingest.",
    )
    parser.add_argument(
        "--collection-name",
        default="sample-knowledge-base",
        help="Logical collection name to create or append to.",
    )
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--chunk-overlap", type=int, default=64)
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    docs_dir = Path(args.docs_dir)
    file_paths = sorted(path for path in docs_dir.iterdir() if path.is_file())
    if not file_paths:
        raise SystemExit(f"No sample documents found in {docs_dir}")

    async with SessionLocal() as db:
        result = await ingest_documents(
            file_paths=file_paths,
            collection_name=args.collection_name,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            db=db,
        )

    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(async_main())
