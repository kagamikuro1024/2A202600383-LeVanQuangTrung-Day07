from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        """Split text into sentences, then group into chunks.
        
        Example:
            text = "Hello. How are you? I'm fine."
            max_sentences = 2
            → ["Hello. How are you?", "I'm fine."]
        """
        if not text:
            return []
        
        # Split on sentence boundaries: ". ", "! ", "? ", or ".\n"
        # Using regex to split while keeping delimiters
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # Group sentences into chunks
        chunks = []
        current_chunk = []
        
        for sentence in sentences:
            current_chunk.append(sentence)
            
            # If reached max sentences per chunk, save and reset
            if len(current_chunk) >= self.max_sentences_per_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        
        # Add remaining sentences as final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        """Entry point: start recursive splitting with default separators."""
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Recursively split text using separators in priority order.
        
        Strategy:
            1. If current text fits chunk_size → return [current_text]
            2. Else try next separator:
               - Split by separator
               - Rejoin small pieces
               - Recursively split large pieces with next separator
            3. If no separators left → split by character
        
        Example:
            text = "Long paragraph\n\nWith sections.\n\nEach part."
            - Try separator "\n\n" → get 2 good chunks
            - If any chunk too big → recurse with "\n"
        """
        # Base case: text fits chunk_size
        if len(current_text) <= self.chunk_size:
            return [current_text]
        
        # No more separators → split by character
        if not remaining_separators:
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]
        
        sep = remaining_separators[0]
        
        # Special case: empty separator means character split
        if sep == "":
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]
        
        # Split by separator
        parts = current_text.split(sep)
        chunks = []
        current = ""
        
        for i, part in enumerate(parts):
            # Try to add part to current chunk
            if current:
                candidate = current + sep + part
            else:
                candidate = part
            
            if len(candidate) <= self.chunk_size:
                # Candidate fits → update current
                current = candidate
            else:
                # Candidate too big → save current, recurse on part
                if current:
                    chunks.append(current)
                
                # If part itself is too big → recurse with next separator
                if len(part) > self.chunk_size:
                    chunks.extend(self._split(part, remaining_separators[1:]))
                else:
                    current = part
        
        # Don't forget the last chunk
        if current:
            chunks.append(current)
        
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    
    Example:
        vec_a = [1, 0, 0]
        vec_b = [0.8, 0.6, 0]
        → dot=0.8, ||a||=1, ||b||=sqrt(0.64+0.36)=1 → similarity=0.8
    """
    # Guard: different lengths or empty vectors
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    
    # Compute dot product using the helper
    dot_product = _dot(vec_a, vec_b)
    
    # Compute magnitudes (norms) using Euclidean norm
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))
    
    # Guard: zero magnitude vectors → similarity is 0
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    
    # Return normalized similarity
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """Chạy 3 chiến lược chunking và so sánh kết quả.
        
        Trả dict với thống kê của mỗi chiến lược:
        {
            "fixed_size": {"count": int, "avg_length": float, "chunks": [...],
            "by_sentences": {...},
            "recursive": {...}
        }
        """
        result = {}
        
        # Chiến lược 1: FixedSizeChunker (chunks cố định kích thước)
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10)
        fixed_chunks = fixed_chunker.chunk(text)
        result["fixed_size"] = {
            "count": len(fixed_chunks),
            "avg_length": sum(len(c) for c in fixed_chunks) / len(fixed_chunks) if fixed_chunks else 0,
            "chunks": fixed_chunks,
        }
        
        # Chiến lược 2: SentenceChunker (chunks theo ranh giới câu)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        sentence_chunks = sentence_chunker.chunk(text)
        result["by_sentences"] = {
            "count": len(sentence_chunks),
            "avg_length": sum(len(c) for c in sentence_chunks) / len(sentence_chunks) if sentence_chunks else 0,
            "chunks": sentence_chunks,
        }
        
        # Chiến lược 3: RecursiveChunker (chia theo separator có thứ tự)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)
        recursive_chunks = recursive_chunker.chunk(text)
        result["recursive"] = {
            "count": len(recursive_chunks),
            "avg_length": sum(len(c) for c in recursive_chunks) / len(recursive_chunks) if recursive_chunks else 0,
            "chunks": recursive_chunks,
        }
        
        return result
