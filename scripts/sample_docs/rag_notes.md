# RAG Implementation Notes

The ingestion pipeline parses uploaded documents, splits them into chunks with overlap, creates embeddings with OpenAI, and upserts vectors into Qdrant.

The query pipeline retrieves candidate chunks, optionally reranks them with Cohere, and streams grounded answers with source citations over Server-Sent Events.
