import json
import re
from pathlib import Path
from dotenv import load_dotenv
from src import (
    FixedSizeChunker, 
    Document, 
    EmbeddingStore,
    KnowledgeBaseAgent,
    LocalEmbedder,
    OpenAIEmbedder
)

load_dotenv()

def mock_llm(prompt):
    start = prompt.find("Context:\n") + 9
    end = prompt.find("\nQuestion:")
    if start > 8 and end > start:
        return prompt[start:end].strip()
    return ""

def extract_law_number(text):
    match = re.search(r'Law\s+(\d+)', text)
    return int(match.group(1)) if match else None

def extract_section(text):
    if 'only the captain' in text.lower():
        return "'Only captain' guidelines"
    elif 'equipment' in text.lower():
        return "Players' Equipment"
    elif 'goalkeeper' in text.lower() and '8' in text:
        return "Goalkeeper Time Rule (New 2025/26)"
    elif 'concussion' in text.lower():
        return "Concussion Substitutions"
    elif 'substitution' in text.lower():
        return "Substitutions"
    return "General Rules"

def is_new_rule(text):
    new_rule_keywords = ['new', '2025/26', 'changed', 'trial', 'eight second', 'concussion']
    return any(keyword in text.lower() for keyword in new_rule_keywords)

def main():
    doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
    text = doc_path.read_text(encoding='utf-8')

    doc = Document(id="doc_1", content=text, metadata={
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "domain": "Football/Soccer"
    })

    chunker = FixedSizeChunker(chunk_size=384, overlap=48)
    chunks = chunker.chunk(doc.content)

    print(f"[TRUNG] Total chunks: {len(chunks)}")
    print(f"[TRUNG] Avg chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} chars")

    print("[TRUNG] Using OpenAI Embedder (text-embedding-3-small)...")
    embedder = OpenAIEmbedder()
    store = EmbeddingStore(collection_name="trung_openai_store", embedding_fn=embedder)

    docs_to_add = []
    for i, chunk in enumerate(chunks):
        law_num = extract_law_number(chunk)
        section = extract_section(chunk)
        is_new = is_new_rule(chunk)
        
        importance = "low"
        if is_new or law_num in [3, 4, 5, 12]:
            importance = "high"
        elif section in ["'Only captain' guidelines", "Concussion Substitutions"]:
            importance = "high"
        else:
            importance = "medium"
            
        tags = []
        if 'captain' in chunk.lower(): tags.append("captain")
        if 'equipment' in chunk.lower(): tags.append("equipment")
        if 'goalkeeper' in chunk.lower(): tags.append("goalkeeper")
        if 'concussion' in chunk.lower(): tags.append("concussion")
        if 'substitute' in chunk.lower(): tags.append("substitution")
            
        metadata = {
            "strategy": "FixedSizeChunker_384_48_Smart",
            "chunk_id": i,
            "source": "Laws-of-the-Game-2025_26_single-pages.md",
            "law_number": law_num if law_num else -1,
            "section": section,
            "is_new_rule_2025_26": is_new,
            "importance": importance,
            "tags": ",".join(tags) 
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
    print("TRUNG - BENCHMARK RESULTS")
    print("="*80)

    results = {}
    print(f"{'#':<3} | {'Query':<30} | {'Score':<6} | {'Top-1 Chunk (Preview)':<40}")
    print("-" * 88)
    
    for q_id, query in enumerate(queries, 1):
        # Lấy Top-1 để lấy Score
        search_results = store.search(query, top_k=1)
        top_score = search_results[0]['score'] if search_results else 0.0
        top_chunk = search_results[0]['content'] if search_results else ""
        
        # Lấy câu trả lời từ Agent
        answer = agent.answer(query, top_k=3)
        
        # In ra màn hình từng dòng của bảng
        chunk_preview = top_chunk[:37].replace('\n', ' ') + "..."
        query_preview = (query[:27] + "...") if len(query) > 30 else query
        print(f"{q_id:<3} | {query_preview:<30} | {top_score:<6.3f} | {chunk_preview:<40}")
        
        results[q_id] = {
            "query": query,
            "answer": answer,
            "score": top_score,
            "strategy": "FixedSizeChunker_384_48_Smart"
        }

    results_file = Path("results_trung.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("-" * 88)
    print(f"\n[OK] Results saved: {results_file}")
    print("INFO: Ban co the copy cot Score o tren de dien vao bao cao REPORT.md")

if __name__ == "__main__":
    main()
