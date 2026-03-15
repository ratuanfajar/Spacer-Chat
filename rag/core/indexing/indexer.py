import os
from typing import List
import hashlib
from collections import defaultdict
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import TiDBVectorStore
from app.config import settings
from .cleaner import clean_documents

class DocumentIndexer:
    def __init__(self):
        """
        Inisialisasi koneksi ke Embedding Model dan Vector DB
        saat class dipanggil.
        """
        print("Proses Indexing")
        
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

    def load_documents(self, folder_path: str):
        """
        Load semua PDF dan tambahkan metadata file-level.
        document_id dibuat per FILE (bukan per halaman).
        """
        print("Membaca dokumen...")

        loader = DirectoryLoader(
            folder_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            recursive=True
        )

        documents = loader.load()
        enriched_docs = []

        for doc in documents:
            source_path = doc.metadata.get("source", "")
            file_name = os.path.basename(source_path)
            matkul_name = os.path.basename(os.path.dirname(source_path))
            page_number = doc.metadata.get("page", 0)

            # document_id per file
            document_id = hashlib.md5(source_path.encode()).hexdigest()

            doc.metadata.update({
                "mata_kuliah": matkul_name,
                "file_name": file_name,
                "source_path": source_path,
                "page_number": page_number,
                "document_id": document_id
            })

            enriched_docs.append(doc)

        print(f"Berhasil memuat {len(enriched_docs)} halaman.")
        return enriched_docs

    def split_documents(self, documents: List):
        """
        Split menjadi chunks dan tambahkan chunk_index
        yang reset per document_id.
        """
        print("Memecah dokumen menjadi chunks...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        chunks = text_splitter.split_documents(documents)

        # chunking_id per document_id
        chunk_counter = defaultdict(int)

        for chunk in chunks:
            doc_id = chunk.metadata["document_id"]

            chunk.metadata["chunk_index"] = chunk_counter[doc_id]
            chunk_counter[doc_id] += 1

        print(f"Dokumen dipecah menjadi {len(chunks)} chunks.")
        return chunks


    def store_to_db(self, chunks: List, batch_size: int = 100):
        """Menyimpan chunks ke Vector Database."""
        if not chunks:
            print("Tidak ada chunk untuk disimpan.")
            return

        print("Menyimpan ke Vector Database...")
        
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            self.vector_db.add_documents(batch) # Otomatis Embedding
            print(f"Batch {i//batch_size + 1} / {(total-1)//batch_size + 1} selesai.") 

        print("Proses selesai. Data berhasil disimpan.")

    def ingest_file(self, file_path: str):
        """Proses dan simpan single file ke vector database."""
        from langchain_community.document_loaders import PyPDFLoader

        print(f"Memproses file: {file_path}")

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        source_path = file_path
        file_name = os.path.basename(source_path)
        matkul_name = os.path.basename(os.path.dirname(source_path))
        document_id = hashlib.md5(source_path.encode()).hexdigest()

        for doc in documents:
            doc.metadata.update({
                "mata_kuliah": matkul_name,
                "file_name": file_name,
                "source_path": source_path,
                "page_number": doc.metadata.get("page", 0),
                "document_id": document_id
            })

        if not documents:
            print("Tidak ada konten yang bisa diproses.")
            return

        cleaned_docs = clean_documents(documents)
        chunks = self.split_documents(cleaned_docs)
        self.store_to_db(chunks)
        print(f"File '{file_name}' berhasil diindeks ({len(chunks)} chunks).")

    def run_indexing(self, source_folder: str):
        """Fungsi utama untuk menjalankan seluruh proses."""
        # Load
        docs = self.load_documents(source_folder)
        
        if not docs:
            print("Tidak ada dokumen ditemukan.")
            return
        
        # Cleaning 
        print("Membersihkan dokumen...")
        cleaned_docs = clean_documents(docs)
            
        # Chungking
        chunks = self.split_documents(cleaned_docs)
            
        # Embedding & Store
        self.store_to_db(chunks)

if __name__ == "__main__":
    indexer = DocumentIndexer()
    indexer.run_indexing("data")