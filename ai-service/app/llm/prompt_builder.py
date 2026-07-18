from typing import List, Dict, Any, Optional

class PromptBuilder:
    """
    Constructs clean prompt templates combining query, retrieved contexts, and metadata.
    """
    @staticmethod
    def build_prompt(query: str, chunks: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Formats retrieved knowledge base chunks, query, and metadata into a clean prompt.
        """
        # Format context segments
        context_strs = []
        for i, chunk in enumerate(chunks):
            source = chunk.get("source", "unknown")
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            chunk_metadata = chunk.get("metadata", {})
            meta_str = f", Meta: {chunk_metadata}" if chunk_metadata else ""
            context_strs.append(
                f"[Document #{i+1}] (Source: {source}, Title: {title}{meta_str})\n{content}\n"
            )
            
        context_block = "\n".join(context_strs) if context_strs else "No relevant contexts retrieved."
        
        # Format additional metadata if passed explicitly
        metadata_block = f"Additional Knowledge Metadata: {metadata}\n" if metadata else ""
        
        prompt = (
            "You are KitchenSync AI, an advanced Back-of-House (BOH) AI assistant designed for high-efficiency restaurant operations.\n"
            "Your goal is to optimize kitchen workflows, reduce food waste, ensure food safety compliance, suggest recipe pairings, and draft supplier orders.\n\n"
            "=== RESTAURANT KNOWLEDGE CONTEXT ===\n"
            f"{context_block}\n"
            f"{metadata_block}"
            "====================================\n\n"
            "=== INSTRUCTIONS ===\n"
            "1. Rely primarily on the RESTAURANT KNOWLEDGE CONTEXT provided above to answer the question.\n"
            "2. If the context does not contain the answer, use your expert culinary and restaurant operations knowledge, but explicitly state that you are doing so.\n"
            "3. Be concise, professional, and directly actionable for kitchen staff.\n"
            "4. Provide measurements, times, and temperatures accurately when available.\n\n"
            f"User Question: {query}\n\n"
            "Detailed Actionable Response:"
        )
        return prompt

