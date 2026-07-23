# Embedding Operations — Generic Reference

Embeddings convert text into dense numerical vectors. They enable semantic search, similarity ranking, clustering, and RAG (Retrieval-Augmented Generation) — finding the most relevant context to include in an LLM prompt.

---

## Core Concepts

```
Text → Embedding Model → Vector [0.12, -0.45, 0.78, ...]  (1536 dimensions for OpenAI)
                                      │
                                 Vector DB (pgvector, Pinecone, Weaviate, Qdrant)
                                      │
                              Similarity search → Top-K results → Feed into LLM prompt
```

**Cosine similarity** is the standard metric — vectors pointing in the same direction are semantically similar, regardless of magnitude.

---

## Generating Embeddings

```typescript
// llm/embedding.service.ts

export class EmbeddingService {
  constructor(private readonly llmRouter: LlmRouterService) {}

  // Single text
  async embed(text: string): Promise<number[]> {
    const vectors = await this.llmRouter.embed([text]);
    return vectors[0];
  }

  // Batch — more efficient than calling one at a time
  async embedBatch(texts: string[]): Promise<number[][]> {
    if (texts.length === 0) return [];
    
    // Chunk into batches of 100 (most providers have per-request limits)
    const BATCH_SIZE = 100;
    const results: number[][] = [];
    
    for (let i = 0; i < texts.length; i += BATCH_SIZE) {
      const batch = texts.slice(i, i + BATCH_SIZE);
      const vectors = await this.llmRouter.embed(batch);
      results.push(...vectors);
    }
    
    return results;
  }
}
```

---

## Text Chunking (for Long Documents)

Embedding models have a token limit. Long documents must be split into overlapping chunks.

```typescript
// llm/chunking.util.ts

export interface Chunk {
  text: string;
  index: number;
  startChar: number;
  endChar: number;
}

export function chunkText(
  text: string,
  options: {
    maxTokens?: number;       // approx 4 chars per token
    overlapTokens?: number;   // overlap prevents context loss at boundaries
    separator?: string;       // prefer splitting on sentence/paragraph boundaries
  } = {},
): Chunk[] {
  const { maxTokens = 512, overlapTokens = 64, separator = '\n\n' } = options;
  
  const maxChars = maxTokens * 4;
  const overlapChars = overlapTokens * 4;
  
  const paragraphs = text.split(separator).filter(p => p.trim().length > 0);
  const chunks: Chunk[] = [];
  let current = '';
  let startChar = 0;
  let index = 0;

  for (const para of paragraphs) {
    if ((current + para).length > maxChars) {
      if (current.length > 0) {
        chunks.push({ text: current.trim(), index: index++, startChar, endChar: startChar + current.length });
        // overlap: keep last N chars as start of next chunk
        const overlap = current.slice(-overlapChars);
        startChar += current.length - overlap.length;
        current = overlap + separator + para;
      } else {
        // Single paragraph too long — force split
        chunks.push({ text: para.slice(0, maxChars), index: index++, startChar, endChar: startChar + maxChars });
        startChar += maxChars;
        current = para.slice(maxChars - overlapChars);
      }
    } else {
      current += (current ? separator : '') + para;
    }
  }

  if (current.trim()) {
    chunks.push({ text: current.trim(), index: index, startChar, endChar: startChar + current.length });
  }

  return chunks;
}
```

---

## Storing in PostgreSQL (pgvector)

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table: document chunks with embeddings
CREATE TABLE document_chunks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id   UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index   INTEGER NOT NULL,
  content       TEXT NOT NULL,
  embedding     vector(1536),       -- dimension matches your model (1536 for OpenAI)
  token_count   INTEGER,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast approximate nearest-neighbor search
CREATE INDEX idx_chunks_embedding ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Cosine similarity search — top 5 most relevant chunks
SELECT 
  dc.id,
  dc.content,
  dc.document_id,
  1 - (dc.embedding <=> $1::vector) AS similarity  -- <=> is cosine distance
FROM document_chunks dc
WHERE 1 - (dc.embedding <=> $1::vector) > 0.75     -- similarity threshold
ORDER BY dc.embedding <=> $1::vector               -- ascending distance = descending similarity
LIMIT 5;
```

---

## Similarity Search Service

```typescript
// llm/semantic-search.service.ts

export interface SearchResult {
  id: string;
  content: string;
  documentId: string;
  similarity: number;
}

export class SemanticSearchService {
  constructor(
    private readonly embeddingService: EmbeddingService,
    private readonly db: DatabaseConnection,
  ) {}

  async search(
    query: string,
    options: {
      limit?: number;
      similarityThreshold?: number;
      filter?: { documentId?: string };
    } = {},
  ): Promise<SearchResult[]> {
    const { limit = 5, similarityThreshold = 0.75 } = options;

    // 1. Embed the query
    const queryVector = await this.embeddingService.embed(query);

    // 2. Find similar chunks
    const results = await this.db.query<SearchResult>(`
      SELECT 
        id,
        content,
        document_id AS "documentId",
        1 - (embedding <=> $1::vector) AS similarity
      FROM document_chunks
      WHERE 1 - (embedding <=> $1::vector) > $2
        ${options.filter?.documentId ? 'AND document_id = $4' : ''}
      ORDER BY embedding <=> $1::vector
      LIMIT $3
    `, [
      `[${queryVector.join(',')}]`,
      similarityThreshold,
      limit,
      ...(options.filter?.documentId ? [options.filter.documentId] : []),
    ]);

    return results;
  }
}
```

---

## RAG Pattern (Retrieval-Augmented Generation)

```typescript
// Use search results to enrich LLM prompts with relevant context

async function answerWithContext(question: string): Promise<string> {
  // 1. Find relevant chunks
  const chunks = await semanticSearch.search(question, { limit: 3, similarityThreshold: 0.7 });
  
  if (chunks.length === 0) {
    // No relevant context found — LLM answers from training data only
    return llmRouter.complete({ prompt: question }).then(r => r.content);
  }

  // 2. Build context-enriched prompt
  const context = chunks
    .map((c, i) => `[Source ${i + 1}]\n${c.content}`)
    .join('\n\n---\n\n');

  const response = await llmRouter.complete({
    systemPrompt: 'Answer questions based only on the provided context. If the context does not contain the answer, say so.',
    prompt: `Context:\n${context}\n\nQuestion: ${question}`,
    metadata: { feature: 'rag-qa' },
  });

  return response.content;
}
```

---

## Caching Embeddings

```typescript
// Embeddings are deterministic — cache aggressively to reduce API costs
// Same text always produces the same vector (for the same model version)

async function embedWithCache(text: string): Promise<number[]> {
  const key = `embed:${createHash('sha256').update(text).digest('hex')}`;
  
  const cached = await cache.get<number[]>(key);
  if (cached) return cached;
  
  const vector = await embeddingService.embed(text);
  await cache.set(key, vector, 86_400 * 7); // cache for 7 days
  return vector;
}
```

---

## Best Practices

| Decision | Recommendation |
|---|---|
| Chunk size | 256–512 tokens with 64-token overlap |
| Embedding model | Smaller/cheaper embed models are usually sufficient (e.g. `text-embedding-3-small`) |
| Similarity threshold | 0.7–0.8 for tight relevance; 0.5–0.65 for broad search |
| Index type | HNSW for large datasets (>100K rows); IVFFlat for smaller |
| Cache embeddings | Yes — same text = same vector, 7-day TTL minimum |
| Re-embedding on update | Only if document content changes meaningfully |
