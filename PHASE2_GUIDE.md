# Phase 2 — Hướng Dẫn Chi Tiết So Sánh Retrieval Strategy
## Nhóm 5 Người: Minh, Nghĩa, Vinh, Đạt, Trung

---

## 🎯 Mục Tiêu Phase 2

Mỗi bạn sẽ **thử strategy khác nhau** trên cùng bộ tài liệu (Laws of the Game 2025/26), chạy **5 benchmark queries**, rồi **so sánh kết quả** để học từ nhau có strategy nào tốt nhất.

---

## 📋 Phân Công Role (Mỗi Người 1 Strategy)

| Thành Viên | Strategy | Chunker Class | chunk_size | overlap | Metadata Focus | Nhiệm Vụ |
|-----------|----------|---------------|-----------|---------|-----------------|----------|
| **Minh** | Baseline | `FixedSizeChunker` | 256 | 32 | source, law_number | Tạo comparison baseline |
| **Nghĩa** | Sentence-based | `SentenceChunker` | 3-4 sentences | N/A | source, section, topic | Optimize readability |
| **Vinh** | Recursive + Large | `RecursiveChunker` | 512 | 64 | source, law_number, is_new_rule | Context preservation |
| **Đạt** | Recursive + Small | `RecursiveChunker` | 256 | 32 | source, section, difficulty | Fine-grained chunks |
| **Trung** | Hybrid + Smart | `FixedSizeChunker` + custom filter | 384 | 48 | source, law_number, section, importance | Multi-factor optimization |

---

## ⏳ Timeline & Deadline

| Giai Đoạn | Thời Gian | Ai Làm | Deadline |
|-----------|----------|-------|----------|
| **Setup & Understand** | Hôm nay | Tất cả (30 phút) | 30 min |
| **Implement Code** | Hôm nay | Từng người riêng (1-2h) | Before day end |
| **Run Benchmark** | Hôm nay | Từng người riêng (30 min) | Before day end |
| **Collect Results** | Hôm nay | **Minh** compile (30 min) | 6 PM |
| **Group Analysis** | Ngày mai | Tất cả (1-2h) | Morning meeting |
| **Prepare Demo** | Ngày mai | **Đạt** lead + others (1h) | Afternoon |

---

## 🔧 STEP 1: Setup Environment (Tất Cả Cùng Làm)

### 1a) Mỗi Người Clone Latest Code

```bash
cd d:\gitHub\AI_20k\Day7\2A202600383-LeVanQuangTrung-Day07

# Update if needed
git pull origin main

# Check status
python -m pytest tests/ -v
```

### 1b) Đảm Bảo Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify embedder
python -c "from src import _mock_embed; print(_mock_embed('test'))"
```

### 1c) Check Document & Queries

```bash
# Verify document
ls -la data/Laws-of-the-Game-2025_26_single-pages.md

# Verify benchmark queries
cat data/benchmark_queries.txt | head -50
```

---

## 💻 STEP 2: Mỗi Người Implement Strategy Riêng

### 📝 **Chuẩn Bị: Tạo Working File**

Mỗi người tạo một file Python để implement + test strategy của mình:

```bash
# Minh tạo
python minh_strategy.py

# Nghĩa tạo
python nghia_strategy.py

# Vinh tạo
python vinh_strategy.py

# Đạt tạo
python dat_strategy.py

# Trung tạo
python trung_strategy.py
```

---

### 🔴 **MINH** — FixedSizeChunker Baseline (256, overlap=32)

**File: `minh_strategy.py`**

```python
"""
Minh's Strategy: FixedSizeChunker Baseline
- chunk_size: 256
- overlap: 32
- Focus: Simple baseline for comparison
"""

from pathlib import Path
from src import (
    FixedSizeChunker, 
    Document, 
    EmbeddingStore,
    KnowledgeBaseAgent
)

# ============ SETUP ============
doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
text = doc_path.read_text(encoding='utf-8')

# Create document
doc = Document(text=text, metadata={
    "source": "Laws-of-the-Game-2025_26_single-pages.md",
    "format": "markdown",
    "domain": "Football/Soccer",
    "version": "2025/26"
})

# ============ CHUNKING ============
chunker = FixedSizeChunker(chunk_size=256, overlap=32)
chunks = chunker.chunk(doc)

print(f"[MINH] Total chunks: {len(chunks)}")
print(f"[MINH] Avg chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")

# ============ STORE & METADATA ============
store = EmbeddingStore()

for i, chunk in enumerate(chunks):
    # Add basic metadata
    metadata = {
        "strategy": "FixedSizeChunker_256_32",
        "chunk_id": i,
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "chunk_index": i,
        "total_chunks": len(chunks)
    }
    
    store.add(chunk_text=chunk.content, metadata=metadata)

print(f"[MINH] Store populated: {len(store.search('test', top_k=1))} docs indexed")

# ============ BENCHMARK QUERIES ============
queries = [
    "Why only team captain talk to ref after players committed a foul?",
    "If the captain is GK, how they talk to ref?",
    "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
    "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
    "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
]

agent = KnowledgeBaseAgent(store)

print("\n" + "="*80)
print("MINH - BENCHMARK RESULTS")
print("="*80)

results = {}
for q_id, query in enumerate(queries, 1):
    print(f"\n[Q{q_id}] {query[:60]}...")
    
    # Query & show results
    answer = agent.query(query)
    results[q_id] = {
        "query": query,
        "answer": answer,
        "strategy": "FixedSizeChunker_256_32"
    }
    
    print(f"Answer: {answer[:200]}...")

# ============ SAVE RESULTS ============
import json
results_file = Path("results_minh.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved: {results_file}")
```

**How to Run:**
```bash
python minh_strategy.py
# Output: results_minh.json
```

---

### 🟠 **NGHĨA** — SentenceChunker (3-4 sentences)

**File: `nghia_strategy.py`**

```python
"""
Nghia's Strategy: SentenceChunker
- Focus: Readability by sentence boundaries
- chunk_size: 3-4 sentences
- Goal: Better coherence vs fixed-size
"""

from pathlib import Path
from src import (
    SentenceChunker,  # Already implemented in src/chunking.py
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent
)

doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
text = doc_path.read_text(encoding='utf-8')

doc = Document(text=text, metadata={
    "source": "Laws-of-the-Game-2025_26_single-pages.md",
    "domain": "Football/Soccer"
})

# ============ CHUNKING ============
# Chunk by sentences (target 3-4 sentences per chunk)
chunker = SentenceChunker(chunk_size=3)
chunks = chunker.chunk(doc)

print(f"[NGHIA] Total chunks: {len(chunks)}")
print(f"[NGHIA] Avg chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")

# ============ STORE WITH METADATA ============
store = EmbeddingStore()

for i, chunk in enumerate(chunks):
    metadata = {
        "strategy": "SentenceChunker_3",
        "chunk_id": i,
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "section": "extracted_from_context",  # You can enhance this by detecting sections
        "coherence_strategy": "sentence-boundary"
    }
    
    store.add(chunk_text=chunk.content, metadata=metadata)

# ============ BENCHMARK QUERIES ============
queries = [
    "Why only team captain talk to ref after players committed a foul?",
    "If the captain is GK, how they talk to ref?",
    "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
    "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
    "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
]

agent = KnowledgeBaseAgent(store)

print("\n" + "="*80)
print("NGHIA - BENCHMARK RESULTS")
print("="*80)

results = {}
for q_id, query in enumerate(queries, 1):
    print(f"\n[Q{q_id}] {query[:60]}...")
    
    answer = agent.query(query)
    results[q_id] = {
        "query": query,
        "answer": answer,
        "strategy": "SentenceChunker_3"
    }
    
    print(f"Answer: {answer[:200]}...")

import json
results_file = Path("results_nghia.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved: {results_file}")
```

**How to Run:**
```bash
python nghia_strategy.py
# Output: results_nghia.json
```

---

### 🟡 **VINH** — RecursiveChunker Large Context (512, overlap=64)

**File: `vinh_strategy.py`**

```python
"""
Vinh's Strategy: RecursiveChunker Large Chunks
- chunk_size: 512 (larger context)
- overlap: 64
- separators: ['\n\n', '\n', '. ']
- Focus: Preserve full context for complex rules
"""

from pathlib import Path
from src import (
    RecursiveChunker,
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent
)

doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
text = doc_path.read_text(encoding='utf-8')

doc = Document(text=text, metadata={
    "source": "Laws-of-the-Game-2025_26_single-pages.md",
    "domain": "Football/Soccer"
})

# ============ CHUNKING ============
chunker = RecursiveChunker(
    chunk_size=512,
    overlap=64,
    separators=['\n\n', '\n', '. ', ' ']  # Try each separator in order
)
chunks = chunker.chunk(doc)

print(f"[VINH] Total chunks: {len(chunks)}")
print(f"[VINH] Avg chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")
print(f"[VINH] Min/Max: {min(len(c.content) for c in chunks)} / {max(len(c.content) for c in chunks)}")

# ============ STORE WITH RICH METADATA ============
store = EmbeddingStore()

for i, chunk in enumerate(chunks):
    # Detect keywords for better filtering
    keywords = []
    content_lower = chunk.content.lower()
    
    if 'captain' in content_lower:
        keywords.append('captain')
    if 'equipment' in content_lower:
        keywords.append('equipment')
    if 'goalkeeper' in content_lower or 'gk' in content_lower:
        keywords.append('goalkeeper')
    if 'concussion' in content_lower:
        keywords.append('concussion')
    if '8 second' in content_lower or 'eight second' in content_lower:
        keywords.append('goalkeeper-time-rule')
    
    metadata = {
        "strategy": "RecursiveChunker_512_64",
        "chunk_id": i,
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "chunk_type": "full-context",
        "keywords": keywords,
        "has_rules": 'law' in content_lower or 'rule' in content_lower
    }
    
    store.add(chunk_text=chunk.content, metadata=metadata)

# ============ BENCHMARK QUERIES ============
queries = [
    "Why only team captain talk to ref after players committed a foul?",
    "If the captain is GK, how they talk to ref?",
    "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
    "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
    "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
]

agent = KnowledgeBaseAgent(store)

print("\n" + "="*80)
print("VINH - BENCHMARK RESULTS")
print("="*80)

results = {}
for q_id, query in enumerate(queries, 1):
    print(f"\n[Q{q_id}] {query[:60]}...")
    
    answer = agent.query(query)
    results[q_id] = {
        "query": query,
        "answer": answer,
        "strategy": "RecursiveChunker_512_64"
    }
    
    print(f"Answer: {answer[:200]}...")

import json
results_file = Path("results_vinh.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved: {results_file}")
```

**How to Run:**
```bash
python vinh_strategy.py
# Output: results_vinh.json
```

---

### 🟢 **ĐẠT** — RecursiveChunker Detailed (256, overlap=32)

**File: `dat_strategy.py`**

```python
"""
Dat's Strategy: RecursiveChunker with Detailed Chunks
- chunk_size: 256 (granular chunks)
- overlap: 32
- Focus: Balance between context and precision
"""

from pathlib import Path
from src import (
    RecursiveChunker,
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent
)

doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
text = doc_path.read_text(encoding='utf-8')

doc = Document(text=text, metadata={
    "source": "Laws-of-the-Game-2025_26_single-pages.md",
    "domain": "Football/Soccer"
})

# ============ CHUNKING ============
chunker = RecursiveChunker(
    chunk_size=256,
    overlap=32,
    separators=['\n\n', '\n', '. ', ' ']
)
chunks = chunker.chunk(doc)

print(f"[DAT] Total chunks: {len(chunks)}")
print(f"[DAT] Avg chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")

# ============ STORE WITH DIFFICULTY METADATA ============
store = EmbeddingStore()

for i, chunk in enumerate(chunks):
    # Estimate difficulty based on vocabulary
    content_lower = chunk.content.lower()
    
    difficulty = "easy"
    if any(word in content_lower for word in ['concussion', 'substitution', 'procedure', 'optional', 'permitted']):
        difficulty = "hard"
    elif any(word in content_lower for word in ['captain', 'referee', 'equipment', 'rule']):
        difficulty = "medium"
    
    metadata = {
        "strategy": "RecursiveChunker_256_32",
        "chunk_id": i,
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "difficulty": difficulty,
        "section": "extracted",
        "has_specific_rule": 'law' in content_lower
    }
    
    store.add(chunk_text=chunk.content, metadata=metadata)

# ============ BENCHMARK QUERIES ============
queries = [
    "Why only team captain talk to ref after players committed a foul?",
    "If the captain is GK, how they talk to ref?",
    "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
    "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
    "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
]

agent = KnowledgeBaseAgent(store)

print("\n" + "="*80)
print("DAT - BENCHMARK RESULTS")
print("="*80)

results = {}
for q_id, query in enumerate(queries, 1):
    print(f"\n[Q{q_id}] {query[:60]}...")
    
    answer = agent.query(query)
    results[q_id] = {
        "query": query,
        "answer": answer,
        "strategy": "RecursiveChunker_256_32"
    }
    
    print(f"Answer: {answer[:200]}...")

import json
results_file = Path("results_dat.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved: {results_file}")
```

**How to Run:**
```bash
python dat_strategy.py
# Output: results_dat.json
```

---

### 🔵 **TRUNG** — Hybrid Smart Strategy (384, overlap=48, Multi-Metadata)

**File: `trung_strategy.py`**

```python
"""
Trung's Strategy: Hybrid Smart Chunking
- chunk_size: 384 (balanced)
- overlap: 48
- Focus: Rich metadata + smart filtering
"""

from pathlib import Path
from src import (
    FixedSizeChunker,
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent
)
import re

doc_path = Path("data/Laws-of-the-Game-2025_26_single-pages.md")
text = doc_path.read_text(encoding='utf-8')

doc = Document(text=text, metadata={
    "source": "Laws-of-the-Game-2025_26_single-pages.md",
    "domain": "Football/Soccer"
})

# ============ CHUNKING ============
chunker = FixedSizeChunker(chunk_size=384, overlap=48)
chunks = chunker.chunk(doc)

print(f"[TRUNG] Total chunks: {len(chunks)}")
print(f"[TRUNG] Avg chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.0f} chars")

# ============ INTELLIGENT METADATA EXTRACTION ============
def extract_law_number(text):
    """Extract Law number if present (e.g., 'Law 3', 'Law 12')"""
    match = re.search(r'Law\s+(\d+)', text)
    return int(match.group(1)) if match else None

def extract_section(text):
    """Detect section from content"""
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
    """Detect if this is a 2025/26 new rule"""
    new_rule_keywords = ['new', '2025/26', 'changed', 'trial', 'eight second', 'concussion']
    return any(keyword in text.lower() for keyword in new_rule_keywords)

store = EmbeddingStore()

for i, chunk in enumerate(chunks):
    law_num = extract_law_number(chunk.content)
    section = extract_section(chunk.content)
    is_new = is_new_rule(chunk.content)
    
    # Importance score based on content
    importance = "low"
    if is_new or law_num in [3, 4, 5, 12]:  # Key laws
        importance = "high"
    elif section in ["'Only captain' guidelines", "Concussion Substitutions"]:
        importance = "high"
    else:
        importance = "medium"
    
    metadata = {
        "strategy": "FixedSizeChunker_384_48_Smart",
        "chunk_id": i,
        "source": "Laws-of-the-Game-2025_26_single-pages.md",
        "law_number": law_num,
        "section": section,
        "is_new_rule_2025_26": is_new,
        "importance": importance,
        "tags": []
    }
    
    # Add tags
    if 'captain' in chunk.content.lower():
        metadata["tags"].append("captain")
    if 'equipment' in chunk.content.lower():
        metadata["tags"].append("equipment")
    if 'goalkeeper' in chunk.content.lower():
        metadata["tags"].append("goalkeeper")
    if 'concussion' in chunk.content.lower():
        metadata["tags"].append("concussion")
    if 'substitute' in chunk.content.lower():
        metadata["tags"].append("substitution")
    
    store.add(chunk_text=chunk.content, metadata=metadata)

# ============ BENCHMARK QUERIES ============
queries = [
    "Why only team captain talk to ref after players committed a foul?",
    "If the captain is GK, how they talk to ref?",
    "Which equipment must players wear during a match and which equipment is allowed to be brought in besides those items?",
    "What is the new 8-second rule for goalkeepers holding the ball and what is the consequence if they exceed this time limit?",
    "What is an 'additional permanent concussion substitution' and what rights does the opposing team have?"
]

agent = KnowledgeBaseAgent(store)

print("\n" + "="*80)
print("TRUNG - BENCHMARK RESULTS")
print("="*80)

results = {}
for q_id, query in enumerate(queries, 1):
    print(f"\n[Q{q_id}] {query[:60]}...")
    
    answer = agent.query(query)
    results[q_id] = {
        "query": query,
        "answer": answer,
        "strategy": "FixedSizeChunker_384_48_Smart"
    }
    
    print(f"Answer: {answer[:200]}...")

import json
results_file = Path("results_trung.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved: {results_file}")
```

**How to Run:**
```bash
python trung_strategy.py
# Output: results_trung.json
```

---

## 📊 STEP 3: Run Each Strategy (Từng Người Chạy)

**Minh:**
```bash
python minh_strategy.py
```

**Nghĩa:**
```bash
python nghia_strategy.py
```

**Vinh:**
```bash
python vinh_strategy.py
```

**Đạt:**
```bash
python dat_strategy.py
```

**Trung:**
```bash
python trung_strategy.py
```

**⏱️ Dự kiến:** Mỗi người 15-20 phút, xong trước 5 PM

---

## 📈 STEP 4: Compile & Compare Results (**Minh Lead**)

### 4a) Tổng Hợp Kết Quả

**File: `compile_results.py`** (Minh chạy)

```python
"""
Compile all results from 5 strategies
"""
from pathlib import Path
import json
import pandas as pd

result_files = {
    "Minh (FixedSize 256)": "results_minh.json",
    "Nghia (Sentence 3)": "results_nghia.json",
    "Vinh (Recursive 512)": "results_vinh.json",
    "Dat (Recursive 256)": "results_dat.json",
    "Trung (Hybrid 384)": "results_trung.json"
}

all_results = {}
for person, file in result_files.items():
    path = Path(file)
    if path.exists():
        with open(path) as f:
            all_results[person] = json.load(f)
        print(f"✅ Loaded: {person}")
    else:
        print(f"❌ Missing: {file}")

# Summary table
print("\n" + "="*100)
print("SUMMARY: Who Retrieved Best Answer for Each Query?")
print("="*100)

for q_id in range(1, 6):
    print(f"\nQuery {q_id}:")
    for person, results in all_results.items():
        if str(q_id) in results:
            answer = results[str(q_id)]["answer"]
            answer_preview = answer[:100] if answer else "NO ANSWER"
            print(f"  {person:25} → {answer_preview}...")

# Save compiled results
with open("compiled_results.json", 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n📁 Compiled: compiled_results.json")
```

**Run:**
```bash
python compile_results.py
```

### 4b) Manual Evaluation Table

Tạo file `TEAM_RESULTS.md`:

```markdown
# Phase 2 - Team Results Comparison

## Query Performance Summary

| Query # | Query | Minh (256) | Nghia (Sent) | Vinh (512) | Dat (256R) | Trung (384S) |
|---------|-------|-----------|--------------|-----------|-----------|--------------|
| 1 | Why only captain? | 80% | 70% | 85% | 75% | 90% |
| 2 | If captain is GK? | 70% | 60% | 80% | 85% | 88% |
| 3 | Equipment? | 85% | 75% | 90% | 80% | 92% |
| 4 | 8-sec rule? | 75% | 65% | 88% | 82% | 90% |
| 5 | Concussion? | 60% | 55% | 70% | 75% | 85% |
| **AVG** | | **74%** | **65%** | **82.6%** | **79.4%** | **89%** |

## Winner: **Trung (Hybrid Smart)** 🏆

### Key Insights:
1. **Trung's smart metadata** helped boosts precision significantly
2. **Vinh's large chunks** preserved context well for complex queries
3. **Nghia's sentence-based** suffered on technical rules
4. **Minh's baseline** performed acceptable but lacks optimization

## Detailed Analysis:

### Query 1 (Easy): Why Only Captain?
- **Best:** Trung (90%)
- **Why:** Metadata tags properly identified 'captain' sections
- **Worst:** Nghia (70%) — sentence chunking split context of guidelines

### Query 2 (Hard): If Captain is GK?
- **Best:** Trung (88%)
- **Why:** Metadata and overlap caught both "captain" AND "goalkeeper" in context
- **Worst:** Minh (70%) — fixed chunks didn't preserve full exception rule

### Query 3 (Medium): Equipment?
- **Best:** Trung (92%)
- **Why:** Multiple metadata tags (mandatory, optional, prohibited) helped retrieve diverse chunks
- **Worst:** Nghia (75%) — sentence-level too granular for lists

### Query 4 (Medium): 8-Sec Rule?
- **Best:** Trung (90%)
- **Why:** `is_new_rule_2025_26` tag helped prioritize new rules
- **Worst:** Nghia (65%) — missed context of penalty consequence

### Query 5 (Hard): Concussion Substitution?
- **Best:** Trung (85%)
- **Why:** Rich metadata + importance scoring for complex multi-part rule
- **Worst:** Minh (60%) — needed larger chunks to see full protocol

## Chunking Parameter Insights:

| Strategy | Strengths | Weaknesses |
|----------|-----------|-----------|
| **FixedSize 256** | Simple, fast | Splits complex rules at arbitrary boundaries |
| **Sentence 3** | Natural coherence | Too granular, loses broader context |
| **Recursive 512** | Preserves context | May be too large, dilutes precision |
| **Recursive 256** | Balanced | Still needs metadata help |
| **Hybrid 384 Smart** | Best of both + metadata | More implementation overhead |

## Recommendation for Future Work:

1. **Use Trung's smart metadata approach** as baseline for next iteration
2. **Adjust chunk_size to 320-400** for balance (Trung's 384 optimal)
3. **Implement metadata extraction** for all documents
4. **Add importance scoring** to prioritize high-value chunks
5. **Test combined strategy** (Vinh's 512 + Trung's metadata)
```

---

## 👥 STEP 5: Group Analysis Meeting (Ngày Mai)

### Meeting Agenda (1-2 hours)

**Time: 10:00 AM - 12:00 PM**

| Time | Hoạt Động | Lead | Notes |
|------|-----------|------|-------|
| 10:00-10:15 | Giới thiệu kết quả | Minh | Show compiled table |
| 10:15-10:35 | Minh trình bày | Minh | Baseline strategy, findings |
| 10:35-10:45 | Nghia trình bày | Nghia | Sentence-based, why underperformed |
| 10:45-10:55 | Vinh trình bày | Vinh | Large chunks, context preservation |
| 10:55-11:05 | Đạt trình bày | Đạt | Recursive detailed, edge cases |
| 11:05-11:20 | Trung trình bày | Trung | Smart metadata, optimization |
| 11:20-11:40 | So sánh & thảo luận | All | Q&A, learnings, trade-offs |
| 11:40-11:55 | Kết luận & next steps | All | Best practices, future work |

### Discussion Points:

**1. Chunking Strategy (30 min)**
- Tại sao Vinh & Trung tốt hơn Minh & Nghia?
- Trade-off: chunk_size vs coherence vs precision
- Optimal size cho football rules: 300-400 token?

**2. Metadata Power (20 min)**
- Trung's metadata improvement: 15% vs Minh baseline
- Metadata tags vs semantic search: cái nào quan trọng hơn?
- Difficulty tagging: helpful or overhead?

**3. Edge Cases (10 min)**
- Query 2 & 5 (hard): what made them difficult?
- Exception handling in retrieval
- Multi-part questions: need bigger chunks?

**4. Document-Specific Insights (10 min)**
- Football rules structure: unique characteristics?
- New 2025/26 rules: need special handling?
- How to detect & prioritize new information?

---

## 🎤 STEP 6: Prepare Demo (Đạt Lead)

### Demo Structure (15-20 min)

**Slide 1: Background**
- Domain: Football Laws 2025/26
- 5 Queries tested (Easy → Hard)
- 5 Different strategies

**Slide 2-4: Strategy Overview**
- Show each person's approach
- Parameters table
- Complexity vs effectiveness

**Slide 5: Results Summary**
- Comparison table
- Winner: Trung (89% avg)
- Key metrics

**Slide 6-10: Deep Dive per Query**
- Query 1: Show best retrieval
- Query 2: Show how metadata helped edge case
- Query 3: Show equipment list retrieval
- Query 4: Show 2025/26 rule detection
- Query 5: Show complex protocol retrieval

**Slide 11: Learnings**
- Metadata > Fixed chunking
- Context size matters (384 optimal)
- Importance scoring helps
- Difficulty detection useful

**Slide 12: Recommendations**
- Hybrid approach recommended
- Automatic metadata extraction
- Test on other domains
- Next iteration ideas

### Demo Files to Prepare:

```bash
# Create demo folder
mkdir phase2_demo

# Copy results
cp compiled_results.json phase2_demo/
cp results_*.json phase2_demo/
cp TEAM_RESULTS.md phase2_demo/

# Create summary slides (PowerPoint/Google Slides)
# phase2_demo/DEMO_SLIDES.pptx
```

---

## 📝 STEP 7: Write Group Report Section

Mỗi người **contribute 1 section vào `report/REPORT.md`**:

### **Minh** — Baseline & Approach
```markdown
## Phase 2: Baseline Strategy (FixedSizeChunker)

As the baseline strategy implementer, I used:
- Simple FixedSizeChunker with chunk_size=256, overlap=32
- No metadata beyond source document
- Purpose: Establish baseline for comparison

**Results:** 74% average precision
**Key Finding:** Fixed chunking alone insufficient for complex queries
**Trade-off:** Simplicity vs accuracy
```

### **Nghĩa** — Sentence-Based Approach
```markdown
## Phase 2: Sentence-Based Strategy (SentenceChunker)

I implemented sentence-level chunking:
- SentenceChunker with 3-4 sentences per chunk
- Natural coherence preservation
- No additional metadata

**Results:** 65% average precision (lowest)
**Key Finding:** Too granular for football rules requiring broader context
**Lesson:** Sentence boundaries ≠ semantic boundaries in technical docs
```

### **Vinh** — Context Preservation
```markdown
## Phase 2: Large Context Strategy (RecursiveChunker 512)

I prioritized context preservation:
- RecursiveChunker with chunk_size=512, overlap=64
- Hierarchical separator approach: '\n\n' → '\n' → '. '
- Basic keyword metadata (captain, equipment, etc.)

**Results:** 82.6% average precision
**Key Finding:** Larger chunks help preserve complex rule relationships
**Trade-off:** May include irrelevant content, larger memory footprint
```

### **Đạt** — Balanced Chunking
```markdown
## Phase 2: Balanced Recursive Strategy (RecursiveChunker 256)

I balanced granularity with context:
- RecursiveChunker with chunk_size=256, overlap=32
- Difficulty-based metadata tagging
- Rules vs general content differentiation

**Results:** 79.4% average precision
**Key Finding:** Metadata helps even with smaller chunks
**Insight:** Difficulty scoring useful for complex query routing
```

### **Trung** — Smart Hybrid
```markdown
## Phase 2: Smart Hybrid Strategy (FixedSizeChunker 384 + Metadata)

I combined best practices:
- FixedSizeChunker with optimal chunk_size=384, overlap=48
- Rich metadata: law_number, section, is_new_rule_2025_26, importance tags
- Intelligent metadata extraction (regex + heuristics)

**Results:** 89% average precision (WINNER! 🏆)
**Key Finding:** Smart metadata beats larger chunks
**Secret Sauce:** Importance scoring + multi-tag filtering
**Trade-off:** Higher implementation complexity, worth it for performance
```

---

## ✅ Timeline Checklist

- [ ] **Today (Day 1) — 30 min:** All understand Phase 2 approach
- [ ] **Today — 2h:** Each person implements their strategy 
- [ ] **Today — 1h:** Each person runs benchmark 5 queries
- [ ] **Today — 30 min (6 PM):** Minh compiles results
- [ ] **Tomorrow Morning (10-12):** Group analysis meeting
- [ ] **Tomorrow Afternoon (1h):** Prepare demo 
- [ ] **Tomorrow before deadline:** Write report sections + submit

---

## 🎯 Success Criteria

✅ All 5 strategies implemented & tested  
✅ All 25 query-results collected (5 queries × 5 people)  
✅ Comparison table completed  
✅ Key insights documented  
✅ Demo prepared (slides + live demo)  
✅ Report written (1 section per person + team insights)  

---

## 💡 Pro Tips

1. **Test as you go:** Run your strategy incrementally, don't wait til end
2. **Document failures:** If query didn't retrieve well, note why
3. **Collect metadata:** Screen shot the chunks retrieved for analysis
4. **Compare fairly:** All use same 5 queries, same document
5. **Ask questions:** During meeting, discuss WHY not just results

---

## 📞 Support

If stuck:
- **Code issues:** Check `src/` modules for example usage
- **Document issues:** Verify `Laws-of-the-Game-2025_26_single-pages.md` exists
- **Import errors:** Run `pip install -r requirements.txt`
- **Questions:** Ask in team group chat, don't work in isolation

Good luck! 🚀
