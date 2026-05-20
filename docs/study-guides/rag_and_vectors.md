# Study Guide: RAG, Embeddings & Vector Databases

This guide covers the fundamental concepts, internal mechanics, and implementation practices for building production-grade Retrieval-Augmented Generation (RAG) pipelines.

---

## 📖 Fundamentals

### What is RAG?
Retrieval-Augmented Generation (RAG) is an architectural pattern that improves LLM responses by retrieving relevant information from external data sources and injecting it into the LLM's prompt context.

### Why does it exist?
- **Reduces Hallucinations**: Grounds LLM responses in verified source documents.
- **Accesses Private Data**: Connects LLMs to proprietary documents without needing model fine-tuning.
- **Updates Information**: Integrates up-to-date data without running expensive retraining cycles.

### Core Concepts
- **Chunking**: Splitting documents into small, coherent text segments to preserve context.
- **Embeddings**: Representing text chunks as numerical vectors that capture semantic meaning.
- **Vector Search**: Querying a database to find vectors that are semantically similar to a query vector.

---

## ⚙️ Internal Working

### Vector Search Mechanics
Vector databases use indexing structures to quickly find matching vectors in multi-dimensional spaces.

```
       [Document Ingestion] 
                │
                ▼ (Chunking)
         [Text Chunks] 
                │
                ▼ (Embeddings API)
        [Dense Vectors] ──► [HNSW Graph Construction]
                                      │
                                      ▼
                             [Qdrant Collection]
```

### HNSW Indexing
Hierarchical Navigable Small World (HNSW) graphs organize vectors into layers of skip-lists:
- **Top Layers**: Contain sparse nodes to allow wide-range search jumps.
- **Bottom Layers**: Contain dense clusters for fine-grained similarity matches.

This structure enables Approximate Nearest Neighbor (ANN) searches, reducing query times from linear complexity ($O(N)$) to logarithmic complexity ($O(\log N)$).

---

## 🛠️ Real Project Usage

### Ingestion Strategy
1. **Document Loading**: Text is parsed from uploaded documents (PDF, TXT, MD, DOCX).
2. **Text Splitting**: Chunks are split using a `RecursiveCharacterTextSplitter` configured with a chunk size of 512 tokens and a 64-token overlap.
3. **Embedding Generation**: Text chunks are converted into 3072-dimension vectors using OpenAI's `text-embedding-3-large` API.
4. **Vector Storage**: Vectors are upserted into Qdrant index collections using Cosine Similarity metrics.

### Query Strategy
1. **Vector Query**: Retrieve `top_k * 3` candidate chunks from Qdrant using ANN search.
2. **Reranking**: Send candidates to the Cohere Rerank API to select the top `top_k` chunks.
3. **Context Injection**: Format the top chunks into the LLM prompt to generate the final response.

---

## 💻 Practical Development Knowledge

### Recommended Libraries
- **Vector Database**: `qdrant-client` (Python client for Qdrant).
- **RAG Framework**: `LlamaIndex` or `LangChain`.
- **Parsing**: `PyMuPDF` (PDF parsing) and `docx2txt` (DOCX parsing).

### Common Pitfalls
1. **Lost in the Middle**: Placing too many context chunks in a prompt can cause LLMs to ignore information in the middle of the context block.
   * *Solution*: Limit retrieval results to the top 5 chunks.
2. **Incorrect Chunk Boundaries**: Splitting text mid-sentence can break semantic context.
   * *Solution*: Use recursive splitters that split text at logical separators like double newlines or punctuation marks.

---

## 🗺️ Learning Path

### 🟢 Beginner
- Learn to convert text strings to embedding vectors.
- Build a simple in-memory vector search script using cosine similarity functions.

### 🟡 Intermediate
- Deploy a local Qdrant container and run document indexing operations.
- Implement recursive character splitters and test retrieval queries.

### 🔴 Advanced
- Build hybrid search pipelines combining keyword queries (BM25) and vector searches.
- Configure reranking engines and evaluate retrieval performance using RAGAS.
