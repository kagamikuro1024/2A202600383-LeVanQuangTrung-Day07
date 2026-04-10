from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        """Initialize RAG agent with a vector store and LLM.
        
        Args:
            store: EmbeddingStore instance to retrieve context from
            llm_fn: Callable that takes a prompt string and returns LLM response
        """
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """Generate answer using RAG pattern.
        
        Steps:
            1. Retrieve top_k relevant chunks from the knowledge base
            2. Concatenate chunks as context
            3. Build a prompt with context and question
            4. Call LLM to generate answer
        
        Args:
            question: The user's question
            top_k: Number of context chunks to retrieve
        
        Returns:
            LLM-generated answer grounded in retrieved context
        """
        # Step 1: Retrieve relevant chunks
        retrieved = self.store.search(question, top_k=top_k)
        
        # Step 2: Concatenate retrieved content as context
        context = "\n---\n".join([result["content"] for result in retrieved])
        
        # Step 3: Build prompt with context
        prompt = f"""You are a helpful assistant. Answer the question using the provided context.

Context:
{context}

Question: {question}

Answer:"""
        
        # Step 4: Call LLM and return answer
        answer = self.llm_fn(prompt)
        return answer
