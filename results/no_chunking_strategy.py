import json
from pathlib import Path
from src import (
    Document, 
    EmbeddingStore,
    KnowledgeBaseAgent,
    LocalEmbedder
)

def mock_llm(prompt):
    start = prompt.find("Context:\n") + 9
    end = prompt.find("\nQuestion:")
    if start > 8 and end > start:
        return prompt[start:end].strip()
    return ""

def main():
    doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
    text = doc_path.read_text(encoding='utf-8')

    # No chunking: The whole text is a single chunk
    chunks = [text]

    print(f"[NO_CHUNKING] Total chunks: {len(chunks)}")
    print(f"[NO_CHUNKING] Avg chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} chars")

    embedder = LocalEmbedder("all-MiniLM-L6-v2")
    store = EmbeddingStore(collection_name="no_chunking_store", embedding_fn=embedder)

    docs_to_add = []
    for i, chunk in enumerate(chunks):
        metadata = {
            "strategy": "NoChunking_Baseline",
            "chunk_id": i,
            "source": "Laws-of-the-Game-2025_26_single-pages.md",
        }
        docs_to_add.append(Document(id=f"chunk_{i}", content=chunk, metadata=metadata))
        
    store.add_documents(docs_to_add)

    queries = [
        "Why only team captain talk to ref after players committed a foul?",
        "If the captain is GK, how they talk to ref?",
        "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
        "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
        "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
    ]

    agent = KnowledgeBaseAgent(store, llm_fn=mock_llm)

    print("\n" + "="*80)
    print("NO_CHUNKING - BENCHMARK RESULTS")
    print("="*80)

    results = {}
    for q_id, query in enumerate(queries, 1):
        answer = agent.answer(query, top_k=1) # Only 1 chunk exists
        results[q_id] = {
            "query": query,
            "answer": answer,
            "strategy": "NoChunking_Baseline"
        }
        preview = answer[:150].replace('\n', ' ') if answer else "NO ANSWER"
        print(f"Q{q_id} Answer preview: {preview}...\n")

    results_file = Path("results_no_chunking.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved: {results_file}")

if __name__ == "__main__":
    main()
