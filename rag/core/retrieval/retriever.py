from typing import List, Tuple
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import TiDBVectorStore
from app.config import settings

class RAGRetriever:
    def __init__(self):
        """
        Membuka koneksi ke Vector DB saat class dipanggil.
        """
        print("Proses Retriever")
        
        # Inisialisasi Model Embedding
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )

        # Koneksi ke Vector Database
        self.vector_db = TiDBVectorStore(
            connection_string=settings.TIDB_CONNECTION_STRING,
            embedding_function=self.embeddings,
            table_name=settings.TABLE_NAME,
            distance_strategy="cosine"
        )

    def search_documents(self, query: str, k: int = 5, score_threshold: float = 0.5) -> List[Tuple[Document, float]]:
        """
        Mencari potongan dokumen (chunks) yang relevan dengan pertanyaan user.
        
        Args:
            query (str): Pertanyaan dari user.
            k (int): Jumlah potongan teks teratas yang ingin diambil.
            score_threshold (float): Batas minimal skor kemiripan (0.0 - 1.0).
            
        Returns:
            List[Tuple[Document, float]]: Kumpulan tuple berisi (dokumen, skor relevansi).
        """
        print(f"Menjawab Pertanyaan: '{query}'...")
        
        # Similarity search ke vector db
        results_with_scores = self.vector_db.similarity_search_with_relevance_scores(
            query, 
            k=k,
            score_threshold=score_threshold
        )
        
        print(f"Pencarian Selesai.")
        return results_with_scores

if __name__ == "__main__":
    retriever = RAGRetriever()
    query = input("Pertanyaan: ")
    dokumen_ditemukan = retriever.search_documents(query, k=5, score_threshold=0.5)
    
    print("\nHasil Pencarian:")

    # Karena return-nya Tuple, kita unpack jadi 'doc' dan 'score'
    for i, (doc, score) in enumerate(dokumen_ditemukan):
        print(f"\n[Dokumen ke-{i+1} | Skor Kemiripan: {score:.4f}]")
        print(doc.page_content)
        print("-" * 30)