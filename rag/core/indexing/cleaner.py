import re
from typing import List
from langchain_core.documents import Document

def clean_text(text: str) -> str:
    # Hapus Nomor Halaman (Angka sendirian di satu baris)
    # Contoh: "12" di akhir halaman slide
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Hapus Artifact "Page X" atau "--- PAGE X ---" 
    text = re.sub(r'--- PAGE \d+ ---', '', text)

    # Hapus URL/Source Gambar yang mengganggu
    # Contoh: "(Image source: https://...)"
    text = re.sub(r'\(Image source:.*?\)', '', text, flags=re.IGNORECASE)

    # Hapus Karakter Null / Control Characters yang bikin error database
    text = text.replace('\x00', '')
    
    # Rapikan Spasi Berlebih 
    # Mengubah "Hello      World" jadi "Hello World"
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Hapus baris kosong berlebihan
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Normalisasi poin
    text = re.sub(r'[❑•▪►]', '-', text)
    

    return text.strip()

def clean_documents(documents: List[Document]) -> List[Document]:
    cleaned_docs = []
    
    for doc in documents:
        cleaned_content = clean_text(doc.page_content)

        if len(cleaned_content) > 10:
            doc.page_content = cleaned_content
            cleaned_docs.append(doc)
            
    return cleaned_docs