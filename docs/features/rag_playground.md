# Feature Specification: RAG Playground

This document provides a technical overview and architectural design for the RAG Playground feature, which demonstrates a production-grade Document Ingestion and Retrieval-Augmented Generation (RAG) pipeline.

---

## 📖 Feature Overview

### Description
The RAG Playground allows developers to upload documents (PDF, TXT, MD, DOCX), parse and split them into chunks, generate high-dimensional embeddings, index them in Qdrant, and perform retrieval-augmented generation queries. It includes a side-by-side comparison mode to contrast LLM outputs generated with and without RAG context.

### User Flow
1. The user navigates to `/playground`.
2. They upload a file, configure chunk size/overlap settings, and click "Ingest".
3. Once ingestion is complete, the collection name appears in the selection menu.
4. The user types a query, toggles "RAG ON / OFF", chooses a model, and clicks "Send".
5. The UI displays the streaming response alongside a retrieval trace panel showing the top-retrieved document chunks and their similarity scores.

### Business Logic
- The system prevents redundant processing by verifying document hashes before starting ingestion.
- The retrieval pipeline ensures high relevance by fetching three times the target number of candidates (`top_k * 3`) and applying Cohere Rerank cross-encoders to select the top `top_k` chunks.

---

## ⚙️ Technical Breakdown

### Internal Architecture & Data Flow

```
[Uploaded Document] 
       │
       ▼ (Parser & Recursive text splitter)
   [Chunks] 
       │
       ▼ (OpenAI text-embedding-3-large)
 [Embeddings (3072-dim)] 
       │
       ▼ (Qdrant ANN Cosine Index)
 [Indexed Vector Store]
```

### Retrieval & Generation Lifecycle (Cache Miss Path)
1. **Query Embeddings**: The user query is converted into a vector using the `text-embedding-3-large` model.
2. **ANN Vector Search**: An approximate nearest neighbor (ANN) query is run against Qdrant to retrieve `top_k * 3` candidates based on Cosine Similarity.
3. **Reranking**: The retrieved candidates are sent to the `Cohere Rerank v3` API to recalculate relevance scores.
4. **Context Construction**: The top `top_k` chunks are assembled into a context block inside the generation prompt.
5. **SSE Output Generation**: The system prompts `gpt-4o-mini` with the context block, streaming tokens back to the client using Server-Sent Events (SSE).

### API Flow
- `POST /v1/rag/ingest`: Accepts files and split settings. Parses and indexes documents, returning the count of processed chunks.
- `POST /v1/rag/query`: Streams generated responses as Server-Sent Events, transmitting text chunks, cited sources, and metadata logs.

### State Management (Zustand Store)
The client-side Zustand store tracks:
- Upload states (e.g., active files, progress, success/failure).
- Available collections list.
- Active collection IDs and model selection configs.
- Streamed responses and retrieved chunk references.

---

## 🧠 Engineering Concepts Behind It

### Embedding Vectors (`text-embedding-3-large`)
- **What it is**: AI models that represent text chunks as dense vectors in a high-dimensional mathematical space, capturing semantic meaning.
- **Why it is used**: `text-embedding-3-large` supports up to 3072 dimensions, providing high accuracy for retrieval tasks.
- **How it works**: Words and phrases with similar meanings are mapped to vectors that are positioned close to each other in the vector space, allowing semantic queries rather than just keyword matches.

### Approximate Nearest Neighbor (ANN) & HNSW
- **What it is**: Algorithms that search for vectors close to a query vector without comparing the query to every vector in the database.
- **Why it is used**: Comparing query vectors to millions of documents manually is too slow for production.
- **How it works**: Hierarchical Navigable Small World (HNSW) graphs organize vectors into layers of skip-lists. Searches navigate through top sparse layers to find the general neighborhood before refining the search in denser layers.

### Cross-Encoder Reranking
- **What it is**: A model that analyzes a query and a retrieved text chunk together to determine a relevance score, rather than comparing pre-computed vectors.
- **Why it is used**: Vector searches (bi-encoders) are fast but lose contextual nuance. Cross-encoders analyze query-document pairs in detail, correcting errors where vector searches match irrelevant text.
- **How it works**: A transformer model processes the query and document chunk simultaneously, outputting a probability score indicating document relevance.

```
          ┌─────────────┐
          │ User Query  │
          └──────┬──────┘
                 ▼
      ┌────────────────────┐
      │  Vector DB (ANN)   │
      └──────────┬─────────┘
                 ▼ (Top 15 candidates)
      ┌────────────────────┐
      │   Cohere Rerank    │ ◄── (Processes query + doc pair)
      └──────────┬─────────┘
                 ▼ (Top 5 reranked docs)
      ┌────────────────────┐
      │   LLM Generator    │
      └────────────────────┘
```

### Best Practices & Performance Optimization
- **Verify Document Hashes**: Calculate MD5 checksums of files before upload, skipping ingestion if the file already exists in the database.
- **Set Up Connection Pools**: Maintain persistent connections to Qdrant to avoid handshake latency overhead.
- **Rerank Selectively**: Only run reranking on retrieved candidate chunks, keeping candidate limits (e.g., `top_k * 3`) reasonable to control latency and API costs.
