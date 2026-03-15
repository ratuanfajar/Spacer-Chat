from typing import Dict, Any, List, Tuple
from langchain_core.documents import Document
from rag.core.retrieval.retriever import RAGRetriever
from rag.core.generation.generator import RAGGenerator


class RAGChain:
    def __init__(self):
        print("Inisialisasi RAG Chain")
        self.retriever = RAGRetriever()
        self.generator = RAGGenerator()

    def _format_context(self, docs: List[Tuple[Document, float]]) -> str:
        """Menggabungkan isi dokumen menjadi context"""
        if not docs:
            return ""

        context_parts = []

        for doc, score in docs:
            context_parts.append(doc.page_content)

        return "\n\n".join(context_parts)

    def run(self, question: str) -> Dict[str, Any]:
        # Retrieve
        docs = self.retriever.search_documents(question)

        if not docs:
            return {
                "content": "Informasi tidak ditemukan dalam konteks yang tersedia.",
                "suggested_questions": []
            }

        # Build Context
        context = self._format_context(docs)

        # Generate Answer
        result = self.generator.generate(
            question=question,
            context=context
        )

        return result